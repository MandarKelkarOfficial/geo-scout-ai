import pytest
import httpx
import respx
from app.services.geocoding import GeocodingService
from app.schemas.response import GeocodingResult
from app.utils.exceptions import ExternalAPIError, LocationNotFoundError
from app.core.config import get_settings

settings = get_settings()

@pytest.mark.asyncio
async def test_geocode_success():
    async with httpx.AsyncClient() as client:
        service = GeocodingService(client)
        
        mock_response = [{
            "lat": "18.551",
            "lon": "73.939",
            "display_name": "Kharadi, Pune, Maharashtra",
            "type": "suburb"
        }]
        
        with respx.mock:
            respx.get(f"{settings.NOMINATIM_BASE_URL}/search").respond(json=mock_response, status_code=200)
            
            result = await service.geocode("Kharadi, Pune")
            
            assert isinstance(result, GeocodingResult)
            assert result.latitude == 18.551
            assert result.longitude == 73.939
            assert result.display_name == "Kharadi, Pune, Maharashtra"
            assert result.place_type == "suburb"

@pytest.mark.asyncio
async def test_geocode_not_found():
    async with httpx.AsyncClient() as client:
        service = GeocodingService(client)
        
        with respx.mock:
            respx.get(f"{settings.NOMINATIM_BASE_URL}/search").respond(json=[], status_code=200)
            
            with pytest.raises(LocationNotFoundError):
                await service.geocode("UnknownPlaceXYZ")

@pytest.mark.asyncio
async def test_geocode_api_error():
    async with httpx.AsyncClient() as client:
        service = GeocodingService(client)
        
        with respx.mock:
            respx.get(f"{settings.NOMINATIM_BASE_URL}/search").respond(status_code=500)
            
            with pytest.raises(ExternalAPIError):
                await service.geocode("Kharadi, Pune")
