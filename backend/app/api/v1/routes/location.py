from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.response import GeocodingResult, WeatherData, PlacesResponse
from app.services.geocoding import GeocodingService
from app.services.weather import WeatherService
from app.services.places import PlacesService
from app.api.deps import get_geocoding_service, get_weather_service, get_places_service, get_db

router = APIRouter()

@router.get("/location/geocode", response_model=GeocodingResult)
async def geocode_location(
    place: str,
    service: GeocodingService = Depends(get_geocoding_service),
    db: AsyncSession = Depends(get_db)
):
    return await service.geocode(place)

@router.get("/location/weather", response_model=WeatherData)
async def get_weather(
    lat: float,
    lon: float,
    label: str,
    service: WeatherService = Depends(get_weather_service),
    db: AsyncSession = Depends(get_db)
):
    return await service.get_current_weather(lat, lon, label)

@router.get("/location/places", response_model=PlacesResponse)
async def get_places(
    lat: float,
    lon: float,
    category: str,
    service: PlacesService = Depends(get_places_service),
    db: AsyncSession = Depends(get_db)
):
    return await service.get_nearby_places(lat, lon, category)
