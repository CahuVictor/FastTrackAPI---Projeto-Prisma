# app/schemas/event_create.py
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Annotated, Any
from datetime import datetime, timezone

class EventCreate(BaseModel):
    @field_validator("title", "description", mode="before")
    @classmethod
    def limpar_texto(cls, v):
        return v.strip().title() if isinstance(v, str) else v
    
    @field_validator("event_date")
    @classmethod
    def ensure_timezone_aware(cls, v: datetime, info: ValidationInfo):
        """
        Garante que o datetime seja offset-aware (tenha tzinfo). Se não, lança erro.
        """
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("event_date must be timezone-aware.", event_date=v) # ("event_date must be timezone-aware (e.g., 2025-06-12T19:00:00Z)")
        return v

    title: Annotated[str, Field(min_length=3, max_length=100, description="Título do evento", json_schema_extra={"example": "Festival de Tecnologia"})]
    description: Annotated[str, Field(description="Descrição detalhada", json_schema_extra={"example": "Evento com oficinas, palestras e música."})]
    event_date: Annotated[datetime, Field(description="Data e hora do evento (UTC)", json_schema_extra={"example": "2025-06-12T19:00:00Z"})]
    city: Annotated[str, Field(description="Cidade onde o evento ocorrerá", json_schema_extra={"example": "Recife"})]
    participants: Annotated[list[str], Field(description="Lista de participantes", json_schema_extra={"example": ["Alice", "Bob", "Carol"]}, default_factory=list)]
    local_id: int | None = None
    forecast_id: int | None = None