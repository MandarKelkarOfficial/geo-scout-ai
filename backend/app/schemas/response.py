from pydantic import BaseModel, ConfigDict

class GeocodingResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    latitude: float
    longitude: float
    display_name: str
    place_type: str | None

class WeatherData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    location: str
    temperature_celsius: float
    condition: str
    humidity: int | None
    wind_speed_kmh: float | None
    feels_like_celsius: float | None = None
    precipitation_mm: float | None = None
    uv_index: float | None = None

class PlaceResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    category: str
    latitude: float
    longitude: float
    distance_meters: float | None

class PlacesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    places: list[PlaceResult]

class SatelliteInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    location: str
    image_url: str | None          # Primary NASA GIBS tile URL
    description: str
    acquisition_date: str | None
    # Tile metadata for frontend
    tile_x: int | None = None
    tile_y: int | None = None
    zoom_level: int | None = None
    osm_tile_url: str | None = None   # OpenStreetMap fallback tile
    layer: str | None = None          # NASA GIBS layer name
    source: str | None = None         # Data source description

class RealEstateListing(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    price: float
    currency: str
    area_sqft: float | None
    location: str
    dealer_name: str | None
    dealer_contact: str | None

class RealEstateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    listings: list[RealEstateListing]
    average_price: float | None
