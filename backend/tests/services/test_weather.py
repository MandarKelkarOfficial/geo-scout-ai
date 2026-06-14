import pytest
import httpx
import respx
from app.services.weather import WeatherService
from app.schemas.response import WeatherData
from app.utils.exceptions import ExternalAPIError
from app.core.config import get_settings

settings = get_settings()

@pytest.mark.asyncio
async def test_get_current_weather_success():
    async with httpx.AsyncClient() as client:
        service = WeatherService(client)
        
        mock_response = {
            "current_weather": {
                "temperature": 32.5,
                "weathercode": 1,
                "windspeed": 10.5
            }
        }
        
        with respx.mock:
            respx.get(f"{settings.OPEN_METEO_BASE_URL}/forecast").respond(json=mock_response, status_code=200)
            
            result = await service.get_current_weather(18.551, 73.939, "Kharadi")
            
            assert isinstance(result, WeatherData)
            assert result.temperature_celsius == 32.5
            assert result.condition == "Partly cloudy"
            assert result.wind_speed_kmh == 10.5

@pytest.mark.asyncio
async def test_get_current_weather_api_error():
    async with httpx.AsyncClient() as client:
        service = WeatherService(client)
        
        with respx.mock:
            respx.get(f"{settings.OPEN_METEO_BASE_URL}/forecast").respond(status_code=500)
            
            with pytest.raises(ExternalAPIError):
                await service.get_current_weather(18.551, 73.939, "Kharadi")
