import pytest
from app.services.satellite import SatelliteService
from app.schemas.response import SatelliteInfo

@pytest.mark.asyncio
async def test_get_satellite_info():
    service = SatelliteService()
    result = await service.get_satellite_info(18.551, 73.939, "Kharadi")
    assert isinstance(result, SatelliteInfo)
    assert result.location == "Kharadi"
    assert "Integration pending" in result.description
    assert result.image_url is None
