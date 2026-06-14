import pytest
import httpx
import respx
from app.services.places import PlacesService
from app.schemas.response import PlacesResponse, PlaceResult
from app.utils.exceptions import ExternalAPIError
from app.core.config import get_settings

settings = get_settings()

@pytest.mark.asyncio
async def test_get_nearby_places_success():
    async with httpx.AsyncClient() as client:
        service = PlacesService(client)
        
        mock_response = {
            "elements": [
                {"lat": 18.552, "lon": 73.940, "tags": {"name": "Tasty Bites"}},
                {"lat": 18.553, "lon": 73.941, "tags": {"name": "Food Corner"}}
            ]
        }
        
        with respx.mock:
            respx.post(settings.OVERPASS_BASE_URL).respond(json=mock_response, status_code=200)
            
            result = await service.get_nearby_places(18.551, 73.939, "restaurant")
            
            assert isinstance(result, PlacesResponse)
            assert len(result.places) == 2
            assert result.places[0].name == "Tasty Bites"
            assert result.places[0].distance_meters is not None

@pytest.mark.asyncio
async def test_get_nearby_places_empty():
    async with httpx.AsyncClient() as client:
        service = PlacesService(client)
        
        mock_response = {
            "elements": []
        }
        
        with respx.mock:
            respx.post(settings.OVERPASS_BASE_URL).respond(json=mock_response, status_code=200)
            
            result = await service.get_nearby_places(18.551, 73.939, "restaurant")
            
            assert isinstance(result, PlacesResponse)
            assert len(result.places) == 0

@pytest.mark.asyncio
async def test_get_nearby_places_api_error():
    async with httpx.AsyncClient() as client:
        service = PlacesService(client)
        
        with respx.mock:
            respx.post(settings.OVERPASS_BASE_URL).respond(status_code=500)
            
            with pytest.raises(ExternalAPIError):
                await service.get_nearby_places(18.551, 73.939, "restaurant")
