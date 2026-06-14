from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Integer, String, Float, Boolean, JSON, Text, ForeignKey, func, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sessions: Mapped[List["ChatSession"]] = relationship("ChatSession", back_populates="user")
    saved_locations: Mapped[List["SavedLocation"]] = relationship("SavedLocation", back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

class ChatSession(TimestampMixin, Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_token: Mapped[str] = mapped_column(String, unique=True, index=True, default=lambda: str(uuid4()))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    title: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="sessions")
    query_logs: Mapped[List["QueryLog"]] = relationship("QueryLog", back_populates="session", cascade="all, delete-orphan")

class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    tools_used: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="query_logs")

class SavedLocation(TimestampMixin, Base):
    __tablename__ = "saved_locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    place_name: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped["User"] = relationship("User", back_populates="saved_locations")

Index("ix_saved_locations_coords", SavedLocation.latitude, SavedLocation.longitude)

class RealEstateListingCache(TimestampMixin, Base):
    __tablename__ = "real_estate_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="INR")
    area_sqft: Mapped[Optional[float]] = mapped_column(Float)
    location_label: Mapped[str] = mapped_column(String, index=True, nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    dealer_name: Mapped[Optional[str]] = mapped_column(String)
    dealer_contact: Mapped[Optional[str]] = mapped_column(String)
    source: Mapped[str] = mapped_column(String, default="manual")
