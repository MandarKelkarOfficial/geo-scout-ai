from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_me_unauthorized():
    # Without a token, /api/v1/auth/me should return 401
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_invalid_endpoint():
    response = client.get("/api/v1/invalid_path_that_does_not_exist")
    assert response.status_code == 404
