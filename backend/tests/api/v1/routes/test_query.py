import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_query_route_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/query", json={"query": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "tools_used" in data

@pytest.mark.asyncio
async def test_query_route_validation_error():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/query", json={}) # Missing query field
    assert response.status_code == 422
