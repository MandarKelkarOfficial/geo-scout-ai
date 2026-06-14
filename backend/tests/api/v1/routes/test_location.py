import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.deps import get_geocoding_service
from app.schemas.response import GeocodingResult
from app.utils.exceptions import LocationNotFoundError

class MockGeocodingService:
    async def geocode(self, place: str):
        if place == "Unknown":
            raise LocationNotFoundError("Not found")
        return GeocodingResult(latitude=1.0, longitude=2.0, display_name="Test", place_type="city")

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_geocoding_service] = lambda: MockGeocodingService()
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_geocode_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/location/geocode?place=Pune")
    assert response.status_code == 200
    assert response.json()["latitude"] == 1.0

@pytest.mark.asyncio
async def test_geocode_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/location/geocode?place=Unknown")
    assert response.status_code == 404
