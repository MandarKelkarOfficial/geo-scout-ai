from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.models import User, ChatSession, QueryLog, SavedLocation
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password
from typing import List, Optional

# ── Users ──────────────────────────────────────────────────────────────

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
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

async def verify_user_password(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

async def update_user(db: AsyncSession, user_id: int, full_name: Optional[str]) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    if full_name is not None:
        user.full_name = full_name
    await db.commit()
    await db.refresh(user)
    return user

# ── Chat Sessions ────────────────────────────────────────────────────────

async def create_chat_session(db: AsyncSession, session_token: str, user_id: Optional[int] = None) -> ChatSession:
    db_session = ChatSession(session_token=session_token, user_id=user_id)
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

async def get_session_by_token(db: AsyncSession, token: str) -> Optional[ChatSession]:
    result = await db.execute(select(ChatSession).where(ChatSession.session_token == token))
    return result.scalar_one_or_none()

async def get_sessions_for_user(db: AsyncSession, user_id: int) -> List[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
    )
    return list(result.scalars().all())

async def update_session_title(db: AsyncSession, session_id: int, title: str) -> None:
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if session and not session.title:
        session.title = title
        await db.commit()

async def rename_session(db: AsyncSession, session_id: int, user_id: int, title: str) -> Optional[ChatSession]:
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return None
    session.title = title
    await db.commit()
    await db.refresh(session)
    return session

async def delete_session(db: AsyncSession, session_id: int, user_id: int) -> bool:
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return False
    await db.delete(session)
    await db.commit()
    return True

async def set_share_token(db: AsyncSession, session_id: int, user_id: int) -> Optional[ChatSession]:
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return None
    if not session.share_token:
        session.share_token = str(uuid4())
    await db.commit()
    await db.refresh(session)
    return session

async def get_session_by_share_token(db: AsyncSession, share_token: str) -> Optional[ChatSession]:
    result = await db.execute(select(ChatSession).where(ChatSession.share_token == share_token))
    return result.scalar_one_or_none()

# ── Query Logs ──────────────────────────────────────────────────────────

async def create_query_log(
    db: AsyncSession,
    session_id: int,
    role: str,
    query_text: str,
    response_text: str = "",
    tools_used: List[str] = None,
    latency_ms: Optional[int] = None
) -> QueryLog:
    db_log = QueryLog(
        session_id=session_id,
        role=role,
        query_text=query_text,
        response_text=response_text,
        tools_used=tools_used or [],
        latency_ms=latency_ms
    )
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def get_history_for_session(db: AsyncSession, session_id: int) -> List[QueryLog]:
    result = await db.execute(
        select(QueryLog)
        .where(QueryLog.session_id == session_id)
        .order_by(QueryLog.created_at.asc())
    )
    return list(result.scalars().all())

# ── Saved Locations ────────────────────────────────────────────────────

async def get_saved_locations(db: AsyncSession, user_id: int) -> List[SavedLocation]:
    result = await db.execute(
        select(SavedLocation).where(SavedLocation.user_id == user_id).order_by(SavedLocation.created_at.desc())
    )
    return list(result.scalars().all())

async def save_location(
    db: AsyncSession,
    user_id: int,
    label: str,
    place_name: str,
    latitude: float,
    longitude: float,
    category: Optional[str] = None
) -> SavedLocation:
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
