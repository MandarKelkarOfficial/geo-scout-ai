"""
Real Estate Service
====================
Searches property listings from the local SQLite DB (loaded from Kaggle CSVs).
Falls back to the static JSON sample file if the DB has no Kaggle rows.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from sqlalchemy import select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RealEstateListingCache
from app.schemas.response import RealEstateResponse, RealEstateListing


class RealEstateService:
    def __init__(self, db: AsyncSession | None = None, client=None):
        self.db = db
        self.client = client
        self._fallback_listings: list[dict] = []
        self._load_fallback()

    # ──────────────────────────────────────────────────────────────────────────
    # Fallback: static JSON (only used when DB is empty)
    # ──────────────────────────────────────────────────────────────────────────

    def _load_fallback(self):
        data_path = os.path.join(os.path.dirname(__file__), "data", "sample_listings.json")
        try:
            with open(data_path, "r") as f:
                self._fallback_listings = json.load(f)
        except Exception:
            self._fallback_listings = []

    # ──────────────────────────────────────────────────────────────────────────
    # Main search — prefers DB, falls back to JSON
    # ──────────────────────────────────────────────────────────────────────────

    async def search_listings(
        self,
        location_label: str,
        min_budget: Optional[float] = None,
        max_budget: Optional[float] = None,
        limit: int = 20,
    ) -> RealEstateResponse:

        if self.db is not None:
            return await self._search_db(location_label, min_budget, max_budget, limit)

        return self._search_fallback(location_label, min_budget, max_budget)

    # ──────────────────────────────────────────────────────────────────────────
    # DB search
    # ──────────────────────────────────────────────────────────────────────────

    async def _search_db(
        self,
        location_label: str,
        min_budget: Optional[float],
        max_budget: Optional[float],
        limit: int,
    ) -> RealEstateResponse:

        # Build WHERE clause dynamically
        conditions = [
            RealEstateListingCache.location_label.ilike(f"%{location_label}%")
        ]
        if min_budget is not None:
            conditions.append(RealEstateListingCache.price >= min_budget)
        if max_budget is not None:
            conditions.append(RealEstateListingCache.price <= max_budget)

        stmt = (
            select(RealEstateListingCache)
            .where(and_(*conditions))
            .order_by(RealEstateListingCache.price)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows: list[RealEstateListingCache] = list(result.scalars().all())

        # If exact match returned nothing, try fuzzy word-by-word match
        if not rows:
            words = [w for w in location_label.split() if len(w) > 2]
            for word in words:
                stmt2 = (
                    select(RealEstateListingCache)
                    .where(RealEstateListingCache.location_label.ilike(f"%{word}%"))
                    .order_by(RealEstateListingCache.price)
                    .limit(limit)
                )
                result2 = await self.db.execute(stmt2)
                rows = list(result2.scalars().all())
                if rows:
                    break

        if not rows:
            return RealEstateResponse(listings=[], average_price=None)

        listings = [
            RealEstateListing(
                title=row.title,
                price=row.price,
                currency=row.currency,
                area_sqft=row.area_sqft,
                location=row.location_label,
                dealer_name=row.dealer_name,
                dealer_contact=row.dealer_contact,
            )
            for row in rows
        ]

        avg_price = sum(l.price for l in listings) / len(listings)
        return RealEstateResponse(listings=listings, average_price=avg_price)

    # ──────────────────────────────────────────────────────────────────────────
    # JSON fallback (pre-Kaggle)
    # ──────────────────────────────────────────────────────────────────────────

    def _search_fallback(
        self,
        location_label: str,
        min_budget: Optional[float],
        max_budget: Optional[float],
    ) -> RealEstateResponse:
        results = []
        for item in self._fallback_listings:
            if location_label.lower() in item.get("location", "").lower():
                price = item.get("price", 0.0)
                if min_budget is not None and price < min_budget:
                    continue
                if max_budget is not None and price > max_budget:
                    continue
                results.append(RealEstateListing(**item))

        avg_price = sum(r.price for r in results) / len(results) if results else None
        return RealEstateResponse(listings=results, average_price=avg_price)
