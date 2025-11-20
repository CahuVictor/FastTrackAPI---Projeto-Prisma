# app\schemas\event_update.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from datetime import datetime

from app.models.event_local_enums import VenueType
from app.models.local import LocalSource

class LocalUpdate(BaseModel):
    location_name: Annotated[str | None, Field(description="Nome do local", min_length=2, json_schema_extra={"example":"Empresa XYZ"})] = None
    capacity: Annotated[int | None, Field(ge=0, json_schema_extra={"example":100}, description="Capacidade máxima de pessoas")] = None
    venue_type: Annotated[VenueType | None, Field(description="Tipo de local (auditório, salão, etc.)")] = None
    is_accessible: Annotated[bool | None, Field(description="Possui acessibilidade", json_schema_extra={"example":False})] = None
    address: Annotated[str | None, Field(min_length=5, json_schema_extra={"example":"Rua Atualizada, 123"}, description="Endereço completo")] = None
    # past_events: Annotated[list[str] | None, Field(description="Histórico de eventos realizados", json_schema_extra={"example":["Evento A", "Evento B"]})] = None
    manually_edited: Annotated[bool, Field(description="Flag indicando se os dados foram alterados manualmente pelo usuário", default=False, json_schema_extra={"example":False})]
    
    external_id: Annotated[str | None, Field(
        None, description="Identifier of this local in the external LocalInfo system"
    )]
    source: Annotated[LocalSource | None, Field(
        None,
        description=(
            "Origin of this Local. If omitted, INTERNAL_SYNC will be used when "
            "coming from sync and MANUAL when created via this API."
        ),
    )]
    is_indoor: Annotated[bool | None, Field(None, description="True if venue is indoors")]
    has_cover: Annotated[bool | None, Field(None, description="True if the area is covered")]
    
    capacity_seated: Annotated[int | None, Field(
        None, description="Maximum seated capacity"
    )]
    capacity_standing: Annotated[int | None, Field(
        None, description="Maximum standing capacity"
    )]
    
    latitude: Annotated[float | None, Field(
        None, description="Latitude coordinate in decimal degrees"
    )]
    longitude: Annotated[float | None, Field(
        None, description="Longitude coordinate in decimal degrees"
    )]
    timezone: Annotated[str | None, Field(
        None, description="IANA timezone for the venue (e.g. 'America/Recife')"
    )]
    
    # ➋  NÃO permita chaves desconhecidas ─ o teste "tipo_invalido" exige 422
    model_config = ConfigDict(extra="forbid")