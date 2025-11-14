# app\schemas\event_update.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from datetime import datetime

class EventUpdate(BaseModel):
    title: Annotated[str | None, Field(min_length=3, max_length=100, description="Novo título do evento.", json_schema_extra={"example": "Encontro de Startups"})] = None
    description: Annotated[str | None, Field(description="Nova descrição do evento.", json_schema_extra={"example": "Evento com networking, pitch e painéis sobre inovação."})] = None
    event_date: Annotated[datetime | None, Field(description="Nova data e hora do evento (UTC)", json_schema_extra={"example": "2025-07-05T14:30:00Z"})] = None
    city: Annotated[str | None, Field(description="Nova cidade do evento.", json_schema_extra={"example": "Olinda"})] = None
    participants: Annotated[list[str] | None, Field(description="Nova lista de participantes.", json_schema_extra={"example": ["Alice", "Bruno", "Carla"]})] = None
    local_id: Annotated[int | None, Field(description="id do local na tabela.")] = None
    forecast_id: Annotated[int | None, Field(description="id do forecast na tabela.")] = None
    
    # ➋  NÃO permita chaves desconhecidas ─ o teste "tipo_invalido" exige 422
    model_config = ConfigDict(extra="forbid")
    
# Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead.
# (Extra keys: 'example'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide 
# at https://errors.pydantic.dev/2.11/migration/