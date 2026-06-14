from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ChatSessionRead(BaseModel):
    id: int
    session_token: str
    user_id: Optional[int]
    title: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class QueryLogRead(BaseModel):
    id: int
    session_id: int
    query_text: str
    response_text: str
    tools_used: List[str]
    latency_ms: Optional[int]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
