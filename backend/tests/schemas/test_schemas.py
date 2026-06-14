import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user import UserCreate, UserRead

def test_user_create_validation():
    # Valid
    user = UserCreate(email="test@example.com", password="password123")
    assert user.email == "test@example.com"
    
    # Invalid email
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", password="password123")
        
    # Password too short
    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", password="short")

def test_user_read_from_attributes():
    class MockUserModel:
        id = 1
        email = "test@example.com"
        full_name = "Test User"
        is_active = True
        created_at = datetime.now()
        
    user_read = UserRead.model_validate(MockUserModel())
    assert user_read.id == 1
    assert user_read.email == "test@example.com"
