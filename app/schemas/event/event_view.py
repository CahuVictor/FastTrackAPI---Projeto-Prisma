# app/schemas/event/event_view.py
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.event.event_create import EventCreate


class EventView(EventCreate):
    """
    Output schema used to expose Event data via HTTP responses.

    It mirrors the domain entity but is free to adjust naming or add/remove
    fields specific to API concerns.
    """

    id: int = Field(description="Unique identifier of the event.")

    views: int = Field(
        default=0,
        description="Number of times this event was viewed.",
    )

    created_at: datetime = Field(
        description="Timestamp when the event was created.",
    )
    
    updated_at: datetime | None = Field(
        default=None,
        description="Timestamp of the last update, if any.",
    )

    # Allow from ORM/domain objects using attribute names
    model_config = ConfigDict(from_attributes=True)
