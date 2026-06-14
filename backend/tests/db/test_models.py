import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.db.models import Base, User, ChatSession, QueryLog, SavedLocation

@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_user_chat_session_query_log_relationships(async_db: AsyncSession):
    # Create User
    user = User(email="test@example.com", hashed_password="pwd")
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)

    # Create ChatSession
    session = ChatSession(user_id=user.id, title="Test Session")
    async_db.add(session)
    await async_db.commit()
    await async_db.refresh(session)

    # Create QueryLog
    log = QueryLog(
        session_id=session.id, 
        query_text="hello", 
        response_text="hi", 
        tools_used=["tool1"]
    )
    async_db.add(log)
    await async_db.commit()
    
    # Refresh to ensure relationships are loaded
    await async_db.refresh(user, ["sessions"])
    await async_db.refresh(session, ["query_logs"])
    
    assert len(user.sessions) == 1
    assert user.sessions[0].id == session.id
    assert len(user.sessions[0].query_logs) == 1
    assert user.sessions[0].query_logs[0].query_text == "hello"

@pytest.mark.asyncio
async def test_saved_location_relationship(async_db: AsyncSession):
    user = User(email="loc@example.com", hashed_password="pwd")
    async_db.add(user)
    await async_db.commit()
    
    loc = SavedLocation(
        user_id=user.id,
        label="Home",
        place_name="Pune",
        latitude=1.0,
        longitude=2.0
    )
    async_db.add(loc)
    await async_db.commit()
    
    await async_db.refresh(user, ["saved_locations"])
    assert len(user.saved_locations) == 1
    assert user.saved_locations[0].label == "Home"

@pytest.mark.asyncio
async def test_anonymous_chat_session(async_db: AsyncSession):
    session = ChatSession(title="Anon Session")
    async_db.add(session)
    await async_db.commit()
    assert session.user_id is None
    assert session.session_token is not None

@pytest.mark.asyncio
async def test_chat_session_cascade_delete(async_db: AsyncSession):
    session = ChatSession(title="Delete Me")
    async_db.add(session)
    await async_db.commit()
    await async_db.refresh(session)
    
    log = QueryLog(session_id=session.id, query_text="Q", response_text="A")
    async_db.add(log)
    await async_db.commit()
    
    # Delete session
    await async_db.delete(session)
    await async_db.commit()
    
    result = await async_db.execute(select(QueryLog).where(QueryLog.id == log.id))
    deleted_log = result.scalars().first()
    assert deleted_log is None

@pytest.mark.asyncio
async def test_user_email_unique_constraint(async_db: AsyncSession):
    user1 = User(email="unique@example.com", hashed_password="pwd")
    async_db.add(user1)
    await async_db.commit()
    
    user2 = User(email="unique@example.com", hashed_password="pwd2")
    async_db.add(user2)
    with pytest.raises(IntegrityError):
        await async_db.commit()
