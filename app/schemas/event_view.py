# app/schemas/event_view.py
from datetime import datetime

from app.schemas.event_create import EventCreate
 
class EventView(EventCreate):
    id: int
    views: int = 0 # (default = 0)
    created_at: datetime
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True  # pydantic v2 (no v1: orm_mode = True)
    