import pytest
from app.services.rag import RAGService

@pytest.mark.asyncio
async def test_search_local_knowledge():
    service = RAGService()
    result = await service.search_local_knowledge("test query")
    assert result == []
