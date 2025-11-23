# app\schemas\event_update.py
from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from datetime import datetime

from app.models.event_local_enums import EventStatus, EventEnvironment

class EventUpdate(BaseModel):
    """
    Input schema for partially updating an Event via HTTP (PATCH).

    All fields are optional. Only provided fields will be applied to the
    target Event entity.
    """
    
    title: Annotated[str | None, Field(min_length=3, max_length=100, description="Novo título do evento.", json_schema_extra={"example": "Encontro de Startups"})] = None # "New event title." - "Startup Meetup"
    description: Annotated[str | None, Field(description="Nova descrição do evento.", json_schema_extra={"example": "Evento com networking, pitch e painéis sobre inovação."})] = None # "New event description." - "Networking, pitches and innovation panels."
    status: Annotated[ EventStatus | None, Field( description="Updated lifecycle status.", json_schema_extra={"example": "published"},),] = None

    start_time: Annotated[ datetime | None, Field( description="New start datetime (timezone-aware).", json_schema_extra={"example": "2025-07-05T14:30:00Z"},),] = None
    end_time: Annotated[ datetime | None, Field( description="New end datetime (timezone-aware).", json_schema_extra={"example": "2025-07-05T18:00:00Z"},),] = None
    timezone: Annotated[ str | None, Field( description="Updated timezone identifier.", json_schema_extra={"example": "America/Recife"}, ),] = None
    
    city: Annotated[str | None, Field(description="Nova cidade do evento.", json_schema_extra={"example": "Olinda"})] = None
    age_restriction: Annotated[str | None, Field(description="Age classification label", json_schema_extra={"example": "Livre"},),] = None
    expected_audience: Annotated[int | None, Field(description="Updated expected audience size.", json_schema_extra={"example": 800},),] = None
    environment: Annotated[EventEnvironment | None, Field(description="Updated environment (indoor/outdoor).", json_schema_extra={"example": "indoor"},),] = None
    
    participants: Annotated[list[str] | None, Field(description="Nova lista de participantes.", json_schema_extra={"example": ["Alice", "Bruno", "Carla"]})] = None # "New list of participants."
    
    # ➋  NÃO permita chaves desconhecidas ─ o teste "tipo_invalido" exige 422
    model_config = ConfigDict(extra="forbid")
    
# Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead.
# (Extra keys: 'example'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide 
# at https://errors.pydantic.dev/2.11/migration/