from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.deps import get_db, get_current_user
from app.db import crud
from app.db.models import User
from app.schemas.chat import ChatSessionRead, QueryLogRead, SharedChatResponse
from pydantic import BaseModel

router = APIRouter(tags=["sessions"])

class RenameRequest(BaseModel):
    title: str

# ── Authenticated session endpoints ─────────────────────────────────────

@router.get("/sessions", response_model=List[ChatSessionRead])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_sessions_for_user(db, current_user.id)

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_session(db, session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or not owned by you")

@router.get("/sessions/{session_id}/history", response_model=List[QueryLogRead])
async def get_history(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify ownership
    sessions = await crud.get_sessions_for_user(db, current_user.id)
    if not any(s.id == session_id for s in sessions):
        raise HTTPException(status_code=404, detail="Session not found")
    return await crud.get_history_for_session(db, session_id)

@router.post("/sessions/{session_id}/share")
async def share_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    session = await crud.set_share_token(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not owned by you")
    return {"share_token": session.share_token}

@router.patch("/sessions/{session_id}/rename", response_model=ChatSessionRead)
async def rename_session(
    session_id: int,
    body: RenameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    session = await crud.rename_session(db, session_id, current_user.id, body.title)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

# ── Public share endpoint ────────────────────────────────────────────────

@router.get("/share/{share_token}", response_model=SharedChatResponse)
async def get_shared_chat(share_token: str, db: AsyncSession = Depends(get_db)):
    session = await crud.get_session_by_share_token(db, share_token)
    if not session:
        raise HTTPException(status_code=404, detail="Shared chat not found")
    messages = await crud.get_history_for_session(db, session.id)
    return SharedChatResponse(title=session.title, messages=messages)
