import httpx
import structlog
from app.schemas.response import PlacesResponse, PlaceResult
from app.utils.exceptions import ExternalAPIError
from app.utils.geo import haversine
from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

class PlacesService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = settings.OVERPASS_BASE_URL

    def _map_category(self, category: str) -> str:
        # Simple mapping to OSM tags, could be expanded
        cat_lower = category.lower()
        if "restaurant" in cat_lower or "food" in cat_lower:
            return "node['amenity'='restaurant']"
        elif "hospital" in cat_lower or "clinic" in cat_lower:
            return "node['amenity'='hospital']"
        elif "school" in cat_lower or "college" in cat_lower:
            return "node['amenity'='school']"
        elif "atm" in cat_lower:
            return "node['amenity'='atm']"
        else:
            return f"node['amenity'='{cat_lower}']" # fallback

    async def get_nearby_places(self, latitude: float, longitude: float, category: str, radius_meters: int = 2000) -> PlacesResponse:
        osm_filter = self._map_category(category)
        query = f"[out:json];{osm_filter}(around:{radius_meters},{latitude},{longitude});out 10;"
        
        try:
            response = await self.client.post(
                self.base_url,
                data={"data": query},
                timeout=settings.REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            logger.error("places_api_error", error=str(e), lat=latitude, lon=longitude, cat=category)
            raise ExternalAPIError(f"Places API error: {e}")

        places = []
        elements = data.get("elements", [])
        for el in elements:
            lat = el.get("lat")
            lon = el.get("lon")
            tags = el.get("tags", {})
            name = tags.get("name", "Unknown")
            
            if lat is not None and lon is not None:
                dist = haversine(latitude, longitude, lat, lon)
                places.append(PlaceResult(
                    name=name,
                    category=category,
                    latitude=lat,
                    longitude=lon,
                    distance_meters=round(dist, 2)
                ))
        
        return PlacesResponse(places=places)
