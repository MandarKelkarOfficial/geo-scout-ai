import pytest
from fastapi import HTTPException
from app.core.security import verify_api_key
from app.core.config import get_settings

def test_verify_api_key_development(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    
    # Should not raise any exception
    assert verify_api_key(None) is None
    assert verify_api_key("some-key") == "some-key"

def test_verify_api_key_production(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    
    # Missing or invalid key should raise 401
    with pytest.raises(HTTPException) as exc:
        verify_api_key("wrong_key")
    assert exc.value.status_code == 401

def test_password_hashing():
    from app.core.security import hash_password, verify_password
    pwd = "my_secret_password"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_password_hashing_salts():
    from app.core.security import hash_password
    pwd = "my_secret_password"
    hash1 = hash_password(pwd)
    hash2 = hash_password(pwd)
    assert hash1 != hash2
    
    settings = get_settings()
    expected_key = getattr(settings, "API_KEY", "geoai-secret-key")
    # Correct key should pass
    assert verify_api_key(expected_key) == expected_key
