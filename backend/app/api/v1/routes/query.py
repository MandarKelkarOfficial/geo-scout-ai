import time
from uuid import uuid4
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.query import QueryRequest, QueryResponse
from app.llm.agent import GeoAIAgent
from app.api.deps import get_agent, get_db, get_optional_user
from app.db import crud
from app.db.models import User
from typing import Optional

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    agent: GeoAIAgent = Depends(get_agent),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    start_ms = int(time.time() * 1000)

    # Resolve or create session
    session = None
    if request.session_token:
        session = await crud.get_session_by_token(db, request.session_token)

    if not session:
        token = request.session_token or str(uuid4())
        session = await crud.create_chat_session(
            db,
            session_token=token,
            user_id=current_user.id if current_user else None
        )

    # Persist user message
    await crud.create_query_log(
        db,
        session_id=session.id,
        role="user",
        query_text=request.query,
        response_text="",
        tools_used=[]
    )

    # Auto-title from first message (60 chars)
    await crud.update_session_title(db, session.id, request.query[:60])

    # Call the agent
    response = await agent.process_query(request.query, request.session_token)

    latency_ms = int(time.time() * 1000) - start_ms

    # Persist assistant response
    await crud.create_query_log(
        db,
        session_id=session.id,
        role="assistant",
        query_text=request.query,
        response_text=response.answer,
        tools_used=response.tools_used,
        latency_ms=latency_ms
    )

    return QueryResponse(
        answer=response.answer,
        data=response.data,
        tools_used=response.tools_used,
        session_token=session.session_token
    )

