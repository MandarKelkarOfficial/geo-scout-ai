from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    session_token: str | None = None

class QueryResponse(BaseModel):
    answer: str
    data: dict | None = None
    tools_used: list[str] = []
    session_token: str | None = None