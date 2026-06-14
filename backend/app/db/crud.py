from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User, ChatSession, QueryLog, SavedLocation
from app.schemas.user import UserCreate
from app.core.security import hash_password
from typing import List, Optional

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    db_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_chat_session(db: AsyncSession, session_token: str, user_id: Optional[int] = None) -> ChatSession:
    db_session = ChatSession(session_token=session_token, user_id=user_id)
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

async def create_query_log(db: AsyncSession, session_id: int, query_text: str, response_text: str, tools_used: List[str], latency_ms: Optional[int] = None) -> QueryLog:
    db_log = QueryLog(
        session_id=session_id,
        query_text=query_text,
        response_text=response_text,
        tools_used=tools_used,
        latency_ms=latency_ms
    )
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def get_saved_locations(db: AsyncSession, user_id: int) -> List[SavedLocation]:
    result = await db.execute(select(SavedLocation).where(SavedLocation.user_id == user_id).order_by(SavedLocation.created_at.desc()))
    return list(result.scalars().all())

async def save_location(db: AsyncSession, user_id: int, label: str, place_name: str, latitude: float, longitude: float, category: Optional[str] = None) -> SavedLocation:
    db_loc = SavedLocation(
        user_id=user_id,
        label=label,
        place_name=place_name,
        latitude=latitude,
        longitude=longitude,
        category=category
    )
    db.add(db_loc)
    await db.commit()
    await db.refresh(db_loc)
    return db_loc
