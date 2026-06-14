import pytest
from unittest.mock import AsyncMock, MagicMock
from app.llm.agent import GeoAIAgent
from app.llm.model_loader import MockLLMProvider
from app.schemas.response import GeocodingResult, WeatherData, RealEstateResponse, RealEstateListing
from app.utils.exceptions import LocationNotFoundError

@pytest.fixture
def agent():
    llm = MockLLMProvider()
    geo = AsyncMock()
    weather = AsyncMock()
    places = AsyncMock()
    sat = AsyncMock()
    realestate = AsyncMock()
    rag = AsyncMock()
    return GeoAIAgent(llm, geo, weather, places, sat, realestate, rag)

@pytest.mark.asyncio
async def test_agent_weather_query(agent):
    agent.geocode.geocode.return_value = GeocodingResult(
        latitude=18.0, longitude=73.0, display_name="Pune", place_type="city"
    )
    agent.weather.get_current_weather.return_value = WeatherData(
        location="Pune", temperature_celsius=32.0, condition="Clear", humidity=None, wind_speed_kmh=10.0
    )
    
    response = await agent.process_query("What is the weather in Pune?")
    assert "get_weather" in response.tools_used
    assert "32.0" in response.answer

@pytest.mark.asyncio
async def test_agent_real_estate_query(agent):
    agent.realestate.search_listings.return_value = RealEstateResponse(
        listings=[RealEstateListing(title="Test", price=1000, currency="INR", area_sqft=100, location="Pune", dealer_name="A", dealer_contact="1")],
        average_price=1000
    )
    
    response = await agent.process_query("I want to buy a house in Pune budget 10")
    assert "search_real_estate" in response.tools_used
    assert "1000" in response.answer

@pytest.mark.asyncio
async def test_agent_location_not_found(agent):
    agent.geocode.geocode.side_effect = LocationNotFoundError("Not found")
    
    response = await agent.process_query("What is the weather in UnknownPlace123?")
    assert "get_weather" in response.tools_used
    assert "Sorry, I couldn't find information" in response.answer
