"""
Real Estate Data Loader
========================
Parses the Kaggle Indian real estate CSVs (Gurgaon, Hyderabad, Kolkata, Mumbai)
and loads them into the local SQLite 'real_estate_listings' table.

Usage:
    python load_real_estate_data.py

Run this ONCE before running generate_training_data.py so the DB has real data.
"""

import asyncio
import csv
import json
import os
import re
import sys
from pathlib import Path

# ── make sure we can import app modules from backend/
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.db.models import Base, RealEstateListingCache

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent.parent / "mlops" / "data"
DB_URL   = "sqlite+aiosqlite:///" + str(Path(__file__).parent.parent / "backend" / "geoai.db")

CSV_FILES = [
    DATA_DIR / "gurgaon_10k.csv",
    DATA_DIR / "hyderabad.csv",
    DATA_DIR / "kolkata.csv",
    DATA_DIR / "mumbai.csv",
]

# ─────────────────────────────────────────────────────────────────────────────
# PRICE PARSING  (handles "2.63 Cr", "69.25 L", "85,000", "Price on Request")
# ─────────────────────────────────────────────────────────────────────────────

def parse_price_to_inr(raw: str) -> float | None:
    """Convert human-readable Indian price string to plain rupees (float)."""
    if not raw:
        return None
    raw = raw.strip().replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "")
    raw = raw.split("-")[0].strip()  # take lower bound of ranges like "2.02 - 2.02 Cr"

    if "price on request" in raw.lower() or "por" in raw.lower():
        return None

    # strip trailing /SqFt, /Bed etc.
    raw = re.sub(r"/\w+", "", raw).strip()

    multiplier = 1.0
    if raw.upper().endswith("CR"):
        multiplier = 1e7
        raw = raw[:-2].strip()
    elif "CRORE" in raw.upper():
        multiplier = 1e7
        raw = re.sub(r"CRORE", "", raw, flags=re.IGNORECASE).strip()
    elif raw.upper().endswith("L") or raw.upper().endswith("LAC") or raw.upper().endswith("LAKH"):
        multiplier = 1e5
        raw = re.sub(r"(LAC|LAKH|L)$", "", raw, flags=re.IGNORECASE).strip()

    try:
        return float(raw) * multiplier
    except ValueError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# AREA PARSING  (handles "1200 sq.ft", "1200", "120 sq.m", etc.)
# ─────────────────────────────────────────────────────────────────────────────

def parse_area_sqft(raw: str) -> float | None:
    if not raw:
        return None
    raw = raw.strip().replace(",", "")
    # extract the first number
    m = re.search(r"[\d.]+", raw)
    if not m:
        return None
    val = float(m.group())
    if "sq.m" in raw.lower() or "sqm" in raw.lower():
        val = val * 10.764  # m² → ft²
    return round(val, 2)


# ─────────────────────────────────────────────────────────────────────────────
# LOCATION PARSER  (the 'location' column is a Python-dict-like string)
# ─────────────────────────────────────────────────────────────────────────────

def parse_locality_from_location(location_str: str) -> tuple[str, str, float | None, float | None]:
    """
    Returns (locality, city, latitude, longitude) from the location dict string.
    Falls back gracefully when keys are absent.
    """
    locality = ""
    city     = ""
    lat      = None
    lon      = None
    try:
        # The column looks like a Python dict with single-quotes; eval it safely
        d = json.loads(location_str.replace("'", '"').replace("None", "null").replace("True","true").replace("False","false"))
        locality = d.get("LOCALITY_NAME", "") or d.get("LOCALITY_WO_CITY", "") or ""
        city     = d.get("CITY_NAME", "") or ""
        lat      = d.get("LATITUDE") or d.get("lat")
        lon      = d.get("LONGITUDE") or d.get("lng") or d.get("lon")
        if lat:  lat = float(lat)
        if lon:  lon = float(lon)
    except Exception:
        pass
    return locality.strip(), city.strip(), lat, lon


# ─────────────────────────────────────────────────────────────────────────────
# ROW → ORM OBJECT
# ─────────────────────────────────────────────────────────────────────────────

def csv_row_to_listing(row: dict, source_file: str) -> RealEstateListingCache | None:
    """Convert a raw CSV row dict to a RealEstateListingCache ORM object."""

    price = parse_price_to_inr(row.get("PRICE", ""))
    if price is None:
        return None  # skip listings with unparseable prices

    # Area — prefer CARPET_SQFT → SUPERBUILTUP_SQFT → AREA
    area_raw = (
        row.get("CARPET_SQFT") or
        row.get("SUPERBUILTUP_SQFT") or
        row.get("BUILTUP_SQFT") or
        row.get("SUPER_SQFT") or
        row.get("AREA", "")
    )
    area = parse_area_sqft(str(area_raw))

    # Location
    locality, city, lat, lon = parse_locality_from_location(row.get("location", "{}"))

    # Fallback city from CITY column
    if not city:
        city = row.get("CITY", "").strip()

    # Build location label: "Locality, City" or just "City"
    if locality and city:
        location_label = f"{locality}, {city}"
    elif locality:
        location_label = locality
    else:
        location_label = city or "India"

    # Title: prefer PROP_HEADING → PROP_NAME → construct from bedrooms + type
    title = (
        row.get("PROP_HEADING") or
        row.get("PROP_NAME") or
        row.get("SOCIETY_NAME") or
        ""
    ).strip()
    if not title:
        bedrooms = row.get("BEDROOM_NUM", "").strip()
        prop_type = row.get("PROPERTY_TYPE", "Property").strip()
        title = f"{bedrooms} BHK {prop_type}" if bedrooms else prop_type

    # Additional metadata stored as source tag
    source_city = Path(source_file).stem.split("_")[0].capitalize()

    return RealEstateListingCache(
        title          = title[:500],
        price          = price,
        currency       = "INR",
        area_sqft      = area,
        location_label = location_label[:300],
        latitude       = lat,
        longitude      = lon,
        dealer_name    = (row.get("CONTACT_NAME") or row.get("CONTACT_COMPANY_NAME") or "").strip()[:200] or None,
        dealer_contact = None,
        source         = f"kaggle_{source_city.lower()}",
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOADER
# ─────────────────────────────────────────────────────────────────────────────

async def load_csv(session: AsyncSession, csv_path: Path, limit: int | None = None) -> tuple[int, int]:
    """Load one CSV file. Returns (inserted, skipped)."""
    inserted = 0
    skipped  = 0

    with open(csv_path, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        batch: list[RealEstateListingCache] = []

        for i, row in enumerate(reader):
            if limit and i >= limit:
                break

            obj = csv_row_to_listing(row, str(csv_path))
            if obj:
                batch.append(obj)
                inserted += 1
            else:
                skipped += 1

            # Flush every 500 rows
            if len(batch) >= 500:
                session.add_all(batch)
                await session.flush()
                batch.clear()

        if batch:
            session.add_all(batch)
            await session.flush()

    return inserted, skipped


async def main():
    print("\n🏠 GeoAI Real Estate Data Loader")
    print(f"   DB: {DB_URL}")
    print(f"   Source: {DATA_DIR}\n")

    # Verify data files exist
    missing = [f for f in CSV_FILES if not f.exists()]
    if missing:
        print("❌ Missing CSV files:")
        for m in missing:
            print(f"   {m}")
        print(f"\nPlease place the CSV files in: {DATA_DIR}")
        return

    # Create engine
    engine = create_async_engine(DB_URL, echo=False)

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Check existing count
    from sqlalchemy import text
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM real_estate_listings WHERE source LIKE 'kaggle_%'"))
        existing = result.scalar()

    if existing and existing > 0:
        print(f"⚠️  Found {existing:,} existing Kaggle rows in DB.")
        answer = input("   Clear existing Kaggle data and reload? [y/N]: ").strip().lower()
        if answer == "y":
            async with engine.begin() as conn:
                await conn.execute(text("DELETE FROM real_estate_listings WHERE source LIKE 'kaggle_%'"))
            print("   ✅ Cleared old Kaggle rows.")
        else:
            print("   Skipping load. Exiting.")
            return

    # Load all CSV files
    SessionFactory = async_sessionmaker(engine, expire_on_commit=False)
    total_inserted = 0
    total_skipped  = 0

    async with SessionFactory() as session:
        async with session.begin():
            for csv_path in CSV_FILES:
                print(f"📂 Loading {csv_path.name}...")
                ins, skp = await load_csv(session, csv_path)
                total_inserted += ins
                total_skipped  += skp
                print(f"   ✅ Inserted: {ins:,}  |  Skipped (no price): {skp:,}")

    # Final summary
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM real_estate_listings"))
        final_count = result.scalar()

    print(f"\n🎉 Done!")
    print(f"   Total inserted : {total_inserted:,}")
    print(f"   Total skipped  : {total_skipped:,}")
    print(f"   DB total rows  : {final_count:,}")
    print(f"\n✅ You can now run: python generate_training_data.py --count 500")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
