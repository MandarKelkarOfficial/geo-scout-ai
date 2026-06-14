import httpx
from fastapi import Depends
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.llm.model_loader import get_llm_provider
from app.services.geocoding import GeocodingService
from app.services.weather import WeatherService
from app.services.places import PlacesService
from app.services.satellite import SatelliteService
from app.services.realestate import RealEstateService
from app.services.rag import RAGService
from app.llm.agent import GeoAIAgent
from app.core.config import get_settings

settings = get_settings()

async def get_httpx_client():
    async with httpx.AsyncClient() as client:
        yield client

def get_geocoding_service(client: httpx.AsyncClient = Depends(get_httpx_client)) -> GeocodingService:
    return GeocodingService(client)

def get_weather_service(client: httpx.AsyncClient = Depends(get_httpx_client)) -> WeatherService:
    return WeatherService(client)

def get_places_service(client: httpx.AsyncClient = Depends(get_httpx_client)) -> PlacesService:
    return PlacesService(client)

def get_satellite_service(client: httpx.AsyncClient = Depends(get_httpx_client)) -> SatelliteService:
    return SatelliteService(client)

def get_realestate_service(client: httpx.AsyncClient = Depends(get_httpx_client)) -> RealEstateService:
    return RealEstateService(client)

def get_rag_service(client: httpx.AsyncClient = Depends(get_httpx_client)) -> RAGService:
    return RAGService(client)

def get_agent(
    geocoding: GeocodingService = Depends(get_geocoding_service),
    weather: WeatherService = Depends(get_weather_service),
    places: PlacesService = Depends(get_places_service),
    satellite: SatelliteService = Depends(get_satellite_service),
    realestate: RealEstateService = Depends(get_realestate_service),
    rag: RAGService = Depends(get_rag_service)
) -> GeoAIAgent:
    llm = get_llm_provider()
    return GeoAIAgent(llm, geocoding, weather, places, satellite, realestate, rag)
