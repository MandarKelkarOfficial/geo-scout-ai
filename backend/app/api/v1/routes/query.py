from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.query import QueryRequest, QueryResponse
from app.llm.agent import GeoAIAgent
from app.api.deps import get_agent, get_db

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    agent: GeoAIAgent = Depends(get_agent),
    db: AsyncSession = Depends(get_db)
):
    return await agent.process_query(request.query, request.session_id)
