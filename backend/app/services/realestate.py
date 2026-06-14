import json
import os
from app.schemas.response import RealEstateResponse, RealEstateListing

class RealEstateService:
    def __init__(self, client=None):
        self.client = client
        self._load_data()

    def _load_data(self):
        data_path = os.path.join(os.path.dirname(__file__), "data", "sample_listings.json")
        try:
            with open(data_path, "r") as f:
                self.listings = json.load(f)
        except Exception:
            self.listings = []

    async def search_listings(self, location_label: str, min_budget: float | None = None, max_budget: float | None = None) -> RealEstateResponse:
        results = []
        for item in self.listings:
            if location_label.lower() in item.get("location", "").lower():
                price = item.get("price", 0.0)
                if min_budget is not None and price < min_budget:
                    continue
                if max_budget is not None and price > max_budget:
                    continue
                results.append(RealEstateListing(**item))
        
        avg_price = None
        if results:
            avg_price = sum(r.price for r in results) / len(results)
            
        return RealEstateResponse(
            listings=results,
            average_price=avg_price
        )
