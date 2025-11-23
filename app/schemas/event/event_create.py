# app/schemas/event_create.py
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Annotated, Any
from datetime import datetime, timezone

from app.models.event_local_enums import EventStatus, EventEnvironment

class EventCreate(BaseModel):
    """
    Input schema for creating a new Event via HTTP.

    This schema is responsible for:
    - validating and normalizing input data;
    - ensuring datetimes are timezone-aware;
    - enforcing simple invariants such as `end_time > start_time`.
    """

    title: Annotated[str, Field(min_length=3, max_length=100, description="Título do evento", json_schema_extra={"example": "Festival de Tecnologia"})] # Event title - "Technology Festival"
    description: Annotated[str, Field(description="Descrição detalhada", json_schema_extra={"example": "Evento com oficinas, palestras e música."})] # "Detailed description of the event" - "Workshops, talks and live music."
    status: Annotated[EventStatus, Field(description="Lifecycle status for this event", json_schema_extra={"example": "draft"}, ),] = EventStatus.DRAFT
    
    start_time: Annotated[datetime, Field(description="Event start datetime (timezone-aware)", json_schema_extra={"example": "2025-06-12T19:00:00Z"},),]
    end_time: Annotated[datetime,Field( description="Event end datetime (timezone-aware)", json_schema_extra={"example": "2025-06-12T22:00:00Z"},),]
    timezone: Annotated[str, Field( description="IANA timezone identifier", json_schema_extra={"example": "America/Recife"},),]
    
    city: Annotated[str, Field(description="Cidade onde o evento ocorrerá", json_schema_extra={"example": "Recife"})] # "City where the event takes place"
    age_restriction: Annotated[str, Field(description="Age classification label", json_schema_extra={"example": "Livre"},),] = "Livre"
    expected_audience: Annotated[int | None, Field( description="Expected/target number of attendees.", json_schema_extra={"example": 500}, ),] = None
    environment: Annotated[EventEnvironment, Field(description="Indoor/outdoor requirement for the event.", json_schema_extra={"example": "unrestricted"},),] = EventEnvironment.UNRESTRICTED
    
    participants: Annotated[list[str], Field(description="Lista de participantes", json_schema_extra={"example": ["Alice", "Bob", "Carol"]}, default_factory=list)] # "List of participant names"
    
    # ------------------------------------------------------------------ #
    # Validators
    # ------------------------------------------------------------------ #
    
    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_and_titlecase(cls, v: Any) -> Any:
        """
        Pre-process textual fields by stripping whitespace and applying
        title case. If the value is not a string, it is returned as-is.
        """
        return v.strip().title() if isinstance(v, str) else v
    
    @field_validator("start_time", "end_time")
    @classmethod
    def ensure_timezone_aware(cls, v: datetime, info: ValidationInfo) -> datetime:
        """
        Ensure that datetime values are timezone-aware.

        Raises:
            ValueError: If the datetime is naive (no tzinfo).
        """
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("event_date must be timezone-aware.", event_date=v) # ("event_date must be timezone-aware (e.g., 2025-06-12T19:00:00Z)")
        return v
    
    @field_validator("end_time")
    @classmethod
    def ensure_end_after_start(cls, v: datetime, info: ValidationInfo) -> datetime:
        """
        Validate that `end_time` is strictly after `start_time` when both
        are present in the model.

        Raises:
            ValueError: If `end_time <= start_time`.
        """
        data = info.data  # current model values (partially built)
        start_time = data.get("start_time")
        if isinstance(start_time, datetime) and v <= start_time:
            raise ValueError("end_time must be greater than start_time")
        return v