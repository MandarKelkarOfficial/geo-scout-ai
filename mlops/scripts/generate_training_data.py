"""
GeoAI Training Data Generator
==============================
Generates tool-call training examples in JSONL format by calling your real APIs.
Each example is a complete conversation: user query → tool call → tool result → final answer.

Usage:
  python generate_training_data.py --output training_data.jsonl --count 500

The output JSONL can be used directly for QLoRA fine-tuning with HuggingFace TRL/Unsloth.
"""

import asyncio
import json
import argparse
import random
import sys
import httpx
from datetime import datetime
from pathlib import Path

# ── allow DB imports from backend/
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

# ──────────────────────────────────────────────────────────────────────────────
# INDIAN CITIES & LOCALITIES (expand this list for more variety)
# ──────────────────────────────────────────────────────────────────────────────
INDIAN_CITIES = [
    "Pune", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata",
    "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore",
    "Thane", "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara",
    "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot",
    "Kalyan-Dombivli", "Vasai-Virar", "Srinagar", "Aurangabad", "Dhanbad",
    "Amritsar", "Navi Mumbai", "Allahabad", "Ranchi", "Howrah", "Coimbatore",
    "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai", "Raipur",
    "Kota", "Guwahati", "Chandigarh", "Solapur", "Hubli-Dharwad", "Bareilly",
    # Localities within Pune
    "Kharadi, Pune", "Hinjewadi, Pune", "Baner, Pune", "Koregaon Park, Pune",
    "Wakad, Pune", "Viman Nagar, Pune", "Hadapsar, Pune", "Kothrud, Pune",
    # Localities within Mumbai
    "Andheri, Mumbai", "Bandra, Mumbai", "Dadar, Mumbai", "Worli, Mumbai",
    "Powai, Mumbai", "Malad, Mumbai", "Thane West", "Navi Mumbai",
    # Localities within Bangalore
    "Whitefield, Bangalore", "Koramangala, Bangalore", "Indiranagar, Bangalore",
    "HSR Layout, Bangalore", "Electronic City, Bangalore", "Jayanagar, Bangalore",
]

REAL_ESTATE_QUERY_TEMPLATES = [
    "Find {bedrooms} BHK apartments in {location}",
    "Show me properties in {location} under {budget_str}",
    "What are the real estate options in {location}?",
    "Search flats for sale in {location}",
    "I'm looking for a house in {location} with budget {budget_str}",
    "List properties available in {location}",
    "{bedrooms} BHK flats in {location}",
    "Find affordable apartments in {location}",
    "Real estate listings near {location}",
    "Show me homes for sale in {location} budget {budget_str}",
    "What's the property market like in {location}?",
    "Any flats or houses for sale in {location}?",
]

AMENITY_CATEGORIES = [
    "restaurant", "hospital", "school", "college", "bank", "atm",
    "pharmacy", "park", "petrol station", "police station", "bus stop",
    "supermarket", "gym", "hotel", "cafe", "library", "post office",
]

SYSTEM_PROMPT = """You are GeoAI-Core, a highly capable geographical assistant focused on India.
You have access to the following tools to retrieve real-time information:
- get_weather: Get current weather for any location
- get_nearby_places: Find hospitals, restaurants, schools, ATMs, and other amenities near a location
- geocode_location: Convert any place name to its latitude and longitude coordinates
- get_satellite_info: Get satellite imagery and land analysis for a location
- search_real_estate: Search property listings by location and budget

IMPORTANT RULES:
1. ALWAYS use a tool when the user asks about weather, places, properties, coordinates, or satellite data. Never make up these facts.
2. When you receive tool results, synthesize them into a clear, helpful, conversational answer.
3. Keep answers concise and well-structured. Use markdown formatting for lists and emphasis."""

BACKEND_BASE = "http://127.0.0.1:8000/api/v1"
DB_URL       = "sqlite+aiosqlite:///./geoai.db"

# ──────────────────────────────────────────────────────────────────────────────
# API CALLERS  (matched to actual backend routes)
# Routes:
#   GET /api/v1/location/geocode?place=<name>           → {latitude, longitude, ...}
#   GET /api/v1/location/weather?lat=&lon=&label=       → WeatherData
#   GET /api/v1/location/places?lat=&lon=&category=     → PlacesResponse
# Real estate has no HTTP route — we query SQLite directly.
# ──────────────────────────────────────────────────────────────────────────────

async def call_geocode(client: httpx.AsyncClient, location: str) -> dict | None:
    """Geocode a place name → lat/lon dict."""
    try:
        r = await client.get(
            f"{BACKEND_BASE}/location/geocode",
            params={"place": location},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"  [geocode error] {location}: {e}")
    return None


async def call_weather(client: httpx.AsyncClient, lat: float, lon: float, label: str) -> dict | None:
    """Fetch weather using lat/lon (after geocoding)."""
    try:
        r = await client.get(
            f"{BACKEND_BASE}/location/weather",
            params={"lat": lat, "lon": lon, "label": label},
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"  [weather error] {label}: {e}")
    return None


async def call_places(client: httpx.AsyncClient, lat: float, lon: float, category: str, location_label: str) -> dict | None:
    """Fetch nearby places using lat/lon (after geocoding)."""
    try:
        r = await client.get(
            f"{BACKEND_BASE}/location/places",
            params={"lat": lat, "lon": lon, "category": category},
            timeout=20,
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"  [places error] {location_label}/{category}: {e}")
    return None


async def call_real_estate_db(location: str, max_budget: float | None = None, limit: int = 8) -> dict | None:
    """Query real estate listings directly from SQLite DB (no HTTP route exists)."""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from sqlalchemy import select, and_
        from app.db.models import RealEstateListingCache

        engine = create_async_engine(DB_URL, echo=False)
        SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

        async with SessionFactory() as session:
            # Try exact match first
            conditions = [RealEstateListingCache.location_label.ilike(f"%{location}%")]
            if max_budget:
                conditions.append(RealEstateListingCache.price <= max_budget)

            stmt = (
                select(RealEstateListingCache)
                .where(and_(*conditions))
                .order_by(RealEstateListingCache.price)
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = list(result.scalars().all())

            # Fuzzy word-by-word fallback
            if not rows:
                for word in [w for w in location.split() if len(w) > 2]:
                    conditions2 = [RealEstateListingCache.location_label.ilike(f"%{word}%")]
                    if max_budget:
                        conditions2.append(RealEstateListingCache.price <= max_budget)
                    stmt2 = (
                        select(RealEstateListingCache)
                        .where(and_(*conditions2))
                        .order_by(RealEstateListingCache.price)
                        .limit(limit)
                    )
                    result2 = await session.execute(stmt2)
                    rows = list(result2.scalars().all())
                    if rows:
                        break

        await engine.dispose()

        if not rows:
            return None

        listings = [
            {
                "title":        r.title,
                "price":        r.price,
                "currency":     r.currency,
                "area_sqft":    r.area_sqft,
                "location":     r.location_label,
                "dealer_name":  r.dealer_name,
                "dealer_contact": r.dealer_contact,
            }
            for r in rows
        ]
        avg = sum(l["price"] for l in listings) / len(listings)
        return {"listings": listings, "average_price": avg}

    except Exception as e:
        print(f"  [realestate db error] {location}: {e}")
        return None



# ──────────────────────────────────────────────────────────────────────────────
# QUERY TEMPLATES
# ──────────────────────────────────────────────────────────────────────────────

WEATHER_QUERIES = [
    "What's the weather like in {city}?",
    "How's the weather in {city} today?",
    "Tell me the current weather in {city}",
    "What is the temperature in {city} right now?",
    "Is it raining in {city}?",
    "What are the weather conditions in {city}?",
    "How hot is it in {city} today?",
    "{city} weather",
    "Current weather {city}",
    "Weather forecast for {city}",
]

PLACES_QUERIES = [
    "Find {category} near {city}",
    "What are the nearest {category} in {city}?",
    "Show me {category} around {city}",
    "I need a {category} near {city}",
    "List {category} near {city}",
    "Are there any {category} near {city}?",
    "Find me nearby {category} in {city}",
    "Search for {category} near {city}",
    "Closest {category} to {city}",
    "{category} near {city}",
]

GEOCODE_QUERIES = [
    "Where is {city}?",
    "What are the coordinates of {city}?",
    "Give me the latitude and longitude of {city}",
    "Locate {city} on the map",
    "What is the exact location of {city}?",
    "Find coordinates for {city}",
    "GPS coordinates of {city}",
    "Show location of {city}",
]

# ──────────────────────────────────────────────────────────────────────────────
# SYNTHESIZE ANSWERS (rule-based, same logic as MockLLMProvider)
# ──────────────────────────────────────────────────────────────────────────────

def synthesize_weather_answer(data: dict) -> str:
    loc = data.get("location", "")
    temp = data.get("temperature_celsius")
    cond = data.get("condition", "Unknown")
    humidity = data.get("humidity")
    wind = data.get("wind_speed_kmh")
    feels = data.get("feels_like_celsius")
    precip = data.get("precipitation_mm")
    uv = data.get("uv_index")

    parts = [f"**Current Weather in {loc}**\n"]
    parts.append(f"**Temperature:** {temp}°C" + (f" (feels like {feels}°C)" if feels else ""))
    parts.append(f"**Condition:** {cond}")
    if humidity is not None:
        parts.append(f"**Humidity:** {humidity}%")
    if wind is not None:
        parts.append(f"**Wind Speed:** {wind} km/h")
    if precip is not None and precip > 0:
        parts.append(f"**Precipitation:** {precip} mm")
    if uv is not None:
        parts.append(f"**UV Index:** {uv}")
    return "\n".join(parts)


def synthesize_places_answer(data: dict, category: str) -> str:
    places = data.get("places", [])
    if not places:
        return f"I couldn't find any {category} nearby. The area may not have mapped results yet."
    lines = [f"**Nearby {category.title()}**\n"]
    for idx, p in enumerate(places[:8], 1):
        name = p.get("name", "Unnamed")
        dist_m = p.get("distance_meters")
        lat_p = p.get("latitude")
        lon_p = p.get("longitude")
        line = f"{idx}. **{name}**"
        if dist_m is not None:
            dist_km = dist_m / 1000 if dist_m > 100 else dist_m
            line += f" — {dist_km:.2f} km away"
        if lat_p and lon_p:
            line += f"\n   📍 {lat_p:.4f}°N, {lon_p:.4f}°E"
        lines.append(line)
    return "\n".join(lines)


def synthesize_real_estate_answer(data: dict, location: str) -> str:
    listings = data.get("listings", [])
    avg = data.get("average_price")
    if not listings:
        return f"I couldn't find any property listings in **{location}** at the moment. The market may not have current listings available."

    lines = [f"**Property Listings in {location}**\n"]
    for idx, p in enumerate(listings[:6], 1):
        title   = p.get("title", "Property")
        price   = p.get("price", 0)
        area    = p.get("area_sqft")
        loc     = p.get("location", location)
        dealer  = p.get("dealer_name")

        # Format price in Crore / Lakh
        if price >= 1e7:
            price_str = f"₹{price/1e7:.2f} Cr"
        elif price >= 1e5:
            price_str = f"₹{price/1e5:.1f} L"
        else:
            price_str = f"₹{price:,.0f}"

        line = f"{idx}. **{title}** — {price_str}"
        if area:
            line += f" | {area:.0f} sq.ft"
        line += f"\n   📍 {loc}"
        if dealer:
            line += f" | Agent: {dealer}"
        lines.append(line)

    if avg:
        if avg >= 1e7:
            avg_str = f"₹{avg/1e7:.2f} Cr"
        elif avg >= 1e5:
            avg_str = f"₹{avg/1e5:.1f} L"
        else:
            avg_str = f"₹{avg:,.0f}"
        lines.append(f"\n📊 **Average Price:** {avg_str}")

    return "\n".join(lines)


def synthesize_geocode_answer(data: dict) -> str:
    name = data.get("display_name", "")
    lat = data.get("latitude")
    lon = data.get("longitude")
    place_type = data.get("place_type", "")
    lines = ["**Location Found**\n"]
    lines.append(f"**{name}**")
    if lat and lon:
        lines.append(f"**Coordinates:** {lat:.5f}°N, {lon:.5f}°E")
    if place_type:
        lines.append(f"**Type:** {place_type}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# EXAMPLE BUILDERS
# ──────────────────────────────────────────────────────────────────────────────

def build_chat_example(user_query: str, tool_name: str, tool_args: dict,
                        tool_result: dict, final_answer: str) -> dict:
    """Build a single training example in chat-template JSONL format."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [{"type": "function", "function": {"name": tool_name, "arguments": json.dumps(tool_args)}}]
            },
            {"role": "tool", "name": tool_name, "content": json.dumps(tool_result)},
            {"role": "assistant", "content": final_answer},
        ]
    }


async def generate_weather_example(client: httpx.AsyncClient, city: str) -> dict | None:
    query = random.choice(WEATHER_QUERIES).format(city=city)
    # Step 1: geocode to get lat/lon
    geo = await call_geocode(client, city)
    if not geo:
        return None
    lat, lon = geo["latitude"], geo["longitude"]
    # Step 2: fetch weather with lat/lon
    data = await call_weather(client, lat, lon, label=city)
    if not data:
        return None
    answer = synthesize_weather_answer(data)
    return build_chat_example(
        user_query=query,
        tool_name="get_weather",
        tool_args={"location": city},
        tool_result=data,
        final_answer=answer
    )


async def generate_places_example(client: httpx.AsyncClient, city: str) -> dict | None:
    category = random.choice(AMENITY_CATEGORIES)
    query = random.choice(PLACES_QUERIES).format(city=city, category=category)
    # Step 1: geocode to get lat/lon
    geo = await call_geocode(client, city)
    if not geo:
        return None
    lat, lon = geo["latitude"], geo["longitude"]
    # Step 2: fetch nearby places with lat/lon
    data = await call_places(client, lat, lon, category, location_label=city)
    if not data:
        return None
    answer = synthesize_places_answer(data, category)
    return build_chat_example(
        user_query=query,
        tool_name="get_nearby_places",
        tool_args={"location": city, "category": category},
        tool_result=data,
        final_answer=answer
    )


async def generate_real_estate_example(client: httpx.AsyncClient,
                                        location: str,
                                        bedrooms: int | None = None,
                                        max_budget: float | None = None) -> dict | None:
    """Generate a search_real_estate training example."""
    bedrooms_str = str(bedrooms) if bedrooms else random.choice(["2", "3", "4", ""])

    # Build a human-readable budget string
    if max_budget:
        if max_budget >= 1e7:
            budget_str = f"\u20b9{max_budget/1e7:.0f} Cr"
        else:
            budget_str = f"\u20b9{max_budget/1e5:.0f} L"
    else:
        budget_str = "any budget"

    template = random.choice(REAL_ESTATE_QUERY_TEMPLATES)
    query = template.format(
        location=location,
        bedrooms=bedrooms_str or "2",
        budget_str=budget_str,
    )

    # Query DB directly (no HTTP route exists for real estate)
    data = await call_real_estate_db(location, max_budget)
    if not data:
        return None

    answer = synthesize_real_estate_answer(data, location)
    return build_chat_example(
        user_query=query,
        tool_name="search_real_estate",
        tool_args={"location": location, "max_budget": max_budget},
        tool_result=data,
        final_answer=answer,
    )


async def generate_geocode_example(client: httpx.AsyncClient, city: str) -> dict | None:
    query = random.choice(GEOCODE_QUERIES).format(city=city)
    data = await call_geocode(client, city)
    if not data:
        return None
    answer = synthesize_geocode_answer(data)
    return build_chat_example(
        user_query=query,
        tool_name="geocode_location",
        tool_args={"location": city},
        tool_result=data,
        final_answer=answer
    )


# ──────────────────────────────────────────────────────────────────────────────
# MAIN GENERATION LOOP
# ──────────────────────────────────────────────────────────────────────────────

# Cities covered by the Kaggle real estate data
KAGGLE_CITIES = [
    "Gurgaon", "Gurugram", "DLF", "Sohna",       # Gurgaon dataset
    "Hyderabad", "Secunderabad", "Kompally",        # Hyderabad dataset
    "Kolkata", "Kolkata South", "Amtala",           # Kolkata dataset
    "Mumbai", "Navi Mumbai", "Thane", "Karjat",     # Mumbai dataset
]

# Budget bands in INR for real-estate query variety
BUDGET_BANDS = [
    None,         # no budget filter
    2_000_000,    # 20 L
    5_000_000,    # 50 L
    10_000_000,   # 1 Cr
    20_000_000,   # 2 Cr
    50_000_000,   # 5 Cr
]


async def generate_dataset(output_path: str, count: int):
    print(f"\n🚀 GeoAI Training Data Generator")
    print(f"   Target: {count} examples → {output_path}")
    print(f"   Backend: {BACKEND_BASE}\n")

    examples = []
    skipped = 0

    # Distribute across tool types: 30% weather, 30% places, 20% geocode, 20% realestate
    targets = {
        "weather":     int(count * 0.30),
        "places":      int(count * 0.30),
        "geocode":     int(count * 0.20),
        "realestate":  int(count * 0.20),
    }

    async with httpx.AsyncClient() as client:
        # ── Weather examples ──────────────────────────────────────────────────
        print(f"📡 Generating {targets['weather']} weather examples...")
        cities_weather = random.choices(INDIAN_CITIES, k=targets["weather"])
        for i, city in enumerate(cities_weather):
            ex = await generate_weather_example(client, city)
            if ex:
                examples.append(ex)
                if (i + 1) % 20 == 0:
                    print(f"   ✅ {i+1}/{targets['weather']} weather examples done")
            else:
                skipped += 1
            await asyncio.sleep(0.3)  # polite rate limit

        # ── Places examples ───────────────────────────────────────────────────
        print(f"\n📍 Generating {targets['places']} places examples...")
        cities_places = random.choices(INDIAN_CITIES, k=targets["places"])
        for i, city in enumerate(cities_places):
            ex = await generate_places_example(client, city)
            if ex:
                examples.append(ex)
                if (i + 1) % 20 == 0:
                    print(f"   ✅ {i+1}/{targets['places']} places examples done")
            else:
                skipped += 1
            await asyncio.sleep(0.5)  # Overpass is rate-limited

        # ── Geocode examples ──────────────────────────────────────────────────
        print(f"\n🌐 Generating {targets['geocode']} geocode examples...")
        cities_geocode = random.choices(INDIAN_CITIES, k=targets["geocode"])
        for i, city in enumerate(cities_geocode):
            ex = await generate_geocode_example(client, city)
            if ex:
                examples.append(ex)
                if (i + 1) % 10 == 0:
                    print(f"   ✅ {i+1}/{targets['geocode']} geocode examples done")
            else:
                skipped += 1
            await asyncio.sleep(1.0)  # Nominatim: max 1 req/sec

        # ── Real-estate examples ──────────────────────────────────────────────
        print(f"\n🏠 Generating {targets['realestate']} real-estate examples...")
        re_cities = random.choices(KAGGLE_CITIES + INDIAN_CITIES, k=targets["realestate"])
        for i, city in enumerate(re_cities):
            budget = random.choice(BUDGET_BANDS)
            bedrooms = random.choice([None, 1, 2, 3, 4])
            ex = await generate_real_estate_example(client, city, bedrooms, budget)
            if ex:
                examples.append(ex)
                if (i + 1) % 10 == 0:
                    print(f"   ✅ {i+1}/{targets['realestate']} real-estate examples done")
            else:
                skipped += 1
            await asyncio.sleep(0.2)

    # Shuffle and save
    random.shuffle(examples)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"\n✅ Done!")
    print(f"   Generated: {len(examples)} examples")
    print(f"   Skipped:   {skipped} (API errors or no data)")
    print(f"   Saved to:  {output_path}")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate GeoAI training data from real APIs")
    parser.add_argument("--output", default="training_data/geoai_train.jsonl", help="Output JSONL file path")
    parser.add_argument("--count", type=int, default=200, help="Number of training examples to generate")
    args = parser.parse_args()

    asyncio.run(generate_dataset(args.output, args.count))
