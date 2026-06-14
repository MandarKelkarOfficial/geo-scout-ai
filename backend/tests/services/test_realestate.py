import pytest
from app.services.realestate import RealEstateService

@pytest.mark.asyncio
async def test_search_listings_location():
    service = RealEstateService()
    result = await service.search_listings("Kharadi")
    assert len(result.listings) >= 2
    assert all("Kharadi" in r.location for r in result.listings)
    assert result.average_price is not None

@pytest.mark.asyncio
async def test_search_listings_budget():
    service = RealEstateService()
    result = await service.search_listings("Pune", max_budget=9000000)
    assert len(result.listings) >= 2
    assert all(r.price <= 9000000 for r in result.listings)

@pytest.mark.asyncio
async def test_search_listings_not_found():
    service = RealEstateService()
    result = await service.search_listings("Mumbai")
    assert len(result.listings) == 0
    assert result.average_price is None
