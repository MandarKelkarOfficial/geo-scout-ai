from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import get_settings
from app.api.v1.routes import health, query, location
from app.utils.exceptions import LocationNotFoundError

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

# Exception handlers
@app.exception_handler(LocationNotFoundError)
async def location_not_found_handler(request: Request, exc: LocationNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )

# CORS middleware allowing all origins in development
if settings.ENVIRONMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(query.router, prefix=settings.API_V1_PREFIX)
app.include_router(location.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {"message": "GeoAI backend running"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=1001, reload=True)