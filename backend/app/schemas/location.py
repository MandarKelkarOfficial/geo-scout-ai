from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class SavedLocationCreate(BaseModel):
    label: str
    place_name: str
    latitude: float
    longitude: float
    category: Optional[str] = None

class SavedLocationRead(SavedLocationCreate):
    id: int
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
