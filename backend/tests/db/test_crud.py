import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db.models import Base
from app.schemas.user import UserCreate
from app.db import crud

@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with TestingSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_and_get_user(async_db):
    user_in = UserCreate(email="test@example.com", password="password123")
    user = await crud.create_user(async_db, user_in)
    assert user.id is not None
    assert user.email == "test@example.com"
    
    # Get user
    fetched_user = await crud.get_user_by_email(async_db, "test@example.com")
    assert fetched_user is not None
    assert fetched_user.id == user.id

@pytest.mark.asyncio
async def test_create_chat_session(async_db):
    session = await crud.create_chat_session(async_db, session_token="token123")
    assert session.id is not None
    assert session.session_token == "token123"

@pytest.mark.asyncio
async def test_query_logs(async_db):
    session = await crud.create_chat_session(async_db, session_token="token456")
    log = await crud.create_query_log(
        async_db,
        session_id=session.id,
        role="assistant",
        query_text="Where is Pune?",
        response_text="Pune is in India.",
        tools_used=["geocoding"],
        latency_ms=150
    )
    assert log.id is not None
    assert log.tools_used == ["geocoding"]
    assert log.role == "assistant"


@pytest.mark.asyncio
async def test_saved_locations(async_db):
    user_in = UserCreate(email="user2@example.com", password="password123")
    user = await crud.create_user(async_db, user_in)
    
    loc = await crud.save_location(
        async_db,
        user_id=user.id,
        label="Home",
        place_name="Kharadi",
        latitude=18.5,
        longitude=73.9
    )
    assert loc.id is not None
    
    locations = await crud.get_saved_locations(async_db, user_id=user.id)
    assert len(locations) == 1
    assert locations[0].label == "Home"
