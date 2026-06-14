class RAGService:
    def __init__(self, client=None):
        self.client = client

    async def search_local_knowledge(self, query: str, top_k: int = 3) -> list[str]:
        # TODO: integrate pgvector/Chroma
        return []
