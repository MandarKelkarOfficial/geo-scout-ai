import httpx
import structlog
from app.schemas.response import GeocodingResult
from app.utils.exceptions import ExternalAPIError, LocationNotFoundError
from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

class GeocodingService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = settings.NOMINATIM_BASE_URL

    async def geocode(self, place_name: str) -> GeocodingResult:
        """Geocode a place name into coordinates using Nominatim API."""
        try:
            response = await self.client.get(
                f"{self.base_url}/search",
                params={"q": place_name, "format": "json", "limit": 1},
                headers={"User-Agent": "GeoAI/1.0"},
                timeout=settings.REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            logger.error("geocoding_api_error", error=str(e), place_name=place_name)
            raise ExternalAPIError(f"Geocoding API error: {e}")

        if not data:
            logger.warning("geocoding_not_found", place_name=place_name)
            raise LocationNotFoundError(f"Location not found: {place_name}")

        result = data[0]
        return GeocodingResult(
            latitude=float(result["lat"]),
            longitude=float(result["lon"]),
            display_name=result.get("display_name", place_name),
            place_type=result.get("type")
        )
