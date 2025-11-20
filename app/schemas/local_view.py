from pydantic import BaseModel, Field, field_validator
from typing import Annotated
from datetime import datetime, timezone

from app.schemas.local_create import LocalCreate
from app.models.event_local_enums import VenueType

class LocalView(LocalCreate):
    id: int
    manually_edited: bool = Field(default=False, description="Flag indicando se os dados foram alterados manualmente pelo usuário")
    created_at: datetime
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True  # pydantic v2 (no v1: orm_mode = True)