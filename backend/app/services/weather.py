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
        """Map WMO weather code to human-readable condition string."""
        if code == 0:
            return "Clear sky"
        elif 1 <= code <= 3:
            return "Partly cloudy"
        elif code in (45, 48):
            return "Foggy"
        elif code in (51, 53, 55):
            return "Drizzle"
        elif code in (61, 63, 65):
            return "Rain"
        elif code in (66, 67):
            return "Freezing rain"
        elif code in (71, 73, 75, 77):
            return "Snow"
        elif code in (80, 81, 82):
            return "Rain showers"
        elif code in (85, 86):
            return "Snow showers"
        elif code in (95, 96, 99):
            return "Thunderstorm"
        return "Unknown"

    async def get_current_weather(self, latitude: float, longitude: float, location_label: str) -> WeatherData:
        """
        Fetches current weather from Open-Meteo (free, no API key).
        Returns temperature, feels-like, humidity, wind speed, precipitation,
        UV index, and a human-readable condition string.
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    # Current weather block
                    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,uv_index",
                    # Also request current_weather for windspeed fallback
                    "current_weather": "true",
                    "timezone": "Asia/Kolkata",
                },
                timeout=settings.REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            logger.error("weather_api_error", error=str(e), lat=latitude, lon=longitude)
            raise ExternalAPIError(f"Weather API error: {e}")

        # Prefer the richer "current" block (new API), fall back to "current_weather"
        current = data.get("current", {})
        legacy = data.get("current_weather", {})

        weather_code = current.get("weather_code") or legacy.get("weathercode", -1)
        condition = self._map_weather_code(int(weather_code))

        temperature = current.get("temperature_2m") or legacy.get("temperature", 0.0)
        feels_like = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")
        wind_speed = current.get("wind_speed_10m") or legacy.get("windspeed")
        precipitation = current.get("precipitation")
        uv_index = current.get("uv_index")

        return WeatherData(
            location=location_label,
            temperature_celsius=round(float(temperature), 1),
            condition=condition,
            humidity=int(humidity) if humidity is not None else None,
            wind_speed_kmh=round(float(wind_speed), 1) if wind_speed is not None else None,
            feels_like_celsius=round(float(feels_like), 1) if feels_like is not None else None,
            precipitation_mm=round(float(precipitation), 1) if precipitation is not None else None,
            uv_index=round(float(uv_index), 1) if uv_index is not None else None,
        )
