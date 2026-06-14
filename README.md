# GeoAI Backend

GeoAI is a geographical question-answering assistant powered by a FastAPI backend. It integrates various location-based services and uses an LLM (Large Language Model) orchestration layer to automatically select and use tools to answer user queries accurately.

## Features
- **Geocoding:** Converts place names into latitude and longitude coordinates using the Nominatim API.
- **Weather:** Retrieves current weather information for any location using the Open-Meteo API.
- **Places Search:** Finds nearby places of specific categories (e.g., restaurants, hospitals) using the Overpass API.
- **Satellite Imagery:** Stubbed integration for fetching satellite imagery (Sentinel Hub).
- **Real Estate:** Mocked service for searching property listings based on location and budget.
- **LLM Orchestration:** An intelligent agent that parses user queries, decides which tools to invoke, and aggregates the results to form a coherent response.
- **Async & Typed:** Fully asynchronous architecture using `httpx` and `asyncio`, strictly typed with Python type hints and Pydantic v2 schemas.
- **Database:** Stores logs of user queries and the tools used via an asynchronous SQLite setup (`aiosqlite` & `SQLAlchemy`).

## Architecture
The application is structured into clearly separated layers:
- `app/api/`: FastAPI route definitions and dependency injection.
- `app/core/`: Configuration and security logic.
- `app/db/`: Database session management and models.
- `app/llm/`: Agent orchestration, model loading, and tool definitions.
- `app/schemas/`: Pydantic models for request validation and structured responses.
- `app/services/`: External API integrations and mock data providers.
- `app/utils/`: Common utilities (e.g., haversine formula, custom exceptions).
