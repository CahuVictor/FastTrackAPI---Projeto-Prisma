from pydantic import BaseModel, Field, field_validator
from typing import Annotated
from datetime import datetime, timezone

from app.schemas.local.local_create import LocalCreate
from app.models.enums import VenueType

class LocalView(LocalCreate):
    id: Annotated[int, Field(description="Identifier of the Local")]
    manually_edited: bool = Field(default=False, description="Flag indicando se os dados foram alterados manualmente pelo usuário")
    created_at: datetime = Field(description="Timestamp when the local was created.")
    updated_at: datetime | None = Field(ndefault=None,description="Timestamp of the last update, if any.",)
    
    class Config:
        from_attributes = True  # pydantic v2 (no v1: orm_mode = True)