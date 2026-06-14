import functools
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "GeoAI"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./geoai.db"
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    NOMINATIM_BASE_URL: str = "https://nominatim.openstreetmap.org"
    OVERPASS_BASE_URL: str = "https://overpass-api.de/api/interpreter"
    LLM_PROVIDER: str = "mock"
    LLM_API_KEY: str | None = None
    LLM_MODEL_NAME: str = "geoai-core-v1"
    REQUEST_TIMEOUT_SECONDS: int = 10

    model_config = SettingsConfigDict(env_file=".env")

@functools.lru_cache()
def get_settings() -> Settings:
    return Settings()
