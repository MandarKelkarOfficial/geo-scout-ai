from fastapi import Header, HTTPException, status
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

def verify_api_key(x_api_key: str | None = Header(default=None)):
    if settings.ENVIRONMENT == "production":
        # In a real application, check against a secure key or database
        # Using a dummy check for now
        expected_key = getattr(settings, "API_KEY", "geoai-secret-key")
        if x_api_key != expected_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API Key"
            )
    return x_api_key

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
