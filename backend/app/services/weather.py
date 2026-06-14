import httpx
import structlog
from app.schemas.response import WeatherData
from app.utils.exceptions import ExternalAPIError
from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

class WeatherService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = settings.OPEN_METEO_BASE_URL

    def _map_weather_code(self, code: int) -> str:
        # 0=Clear sky, 1-3=Partly cloudy, 45/48=Fog, 51-67=Rain/Drizzle, 71-77=Snow, 80-99=Thunderstorm
        if code == 0:
            return "Clear sky"
        elif 1 <= code <= 3:
            return "Partly cloudy"
        elif code in (45, 48):
            return "Fog"
        elif 51 <= code <= 67:
            return "Rain or Drizzle"
        elif 71 <= code <= 77:
            return "Snow"
        elif 80 <= code <= 99:
            return "Thunderstorm"
        return "Unknown"

    async def get_current_weather(self, latitude: float, longitude: float, location_label: str) -> WeatherData:
        try:
            response = await self.client.get(
                f"{self.base_url}/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current_weather": "true"
                },
                timeout=settings.REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            logger.error("weather_api_error", error=str(e), lat=latitude, lon=longitude)
            raise ExternalAPIError(f"Weather API error: {e}")

        current = data.get("current_weather", {})
        condition = self._map_weather_code(current.get("weathercode", -1))
        
        return WeatherData(
            location=location_label,
            temperature_celsius=current.get("temperature", 0.0),
            condition=condition,
            humidity=None,  # Not provided by default in current_weather
            wind_speed_kmh=current.get("windspeed")
        )
