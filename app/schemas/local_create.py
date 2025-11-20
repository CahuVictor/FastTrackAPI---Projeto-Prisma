from pydantic import BaseModel, Field, field_validator
from typing import Annotated

from app.models.event_local_enums import VenueType
from app.models.local import LocalSource

class LocalCreate(BaseModel):
    location_name: Annotated[str, Field(description="Nome do local", min_length=2, json_schema_extra={"example":"CESAR"})]
    capacity: Annotated[int, Field(ge=0, description="Capacidade máxima de pessoas", json_schema_extra={"example":150}, default=1)]  # >= 1
    venue_type: Annotated[VenueType | None, Field(description="Tipo de local (auditório, salão, etc.)", default=None)]
    is_accessible: Annotated[bool, Field(description="Possui acessibilidade", default=False)]
    address: Annotated[str | None, Field(description="Endereço completo", min_length=5, json_schema_extra={"example":"Rua das Flores, 456"}, default=None)]
    
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
    
    @field_validator("location_name", mode="before")
    @classmethod
    def normalizar_nome_local(cls, v):
        if not isinstance(v, str):
            raise TypeError("O campo 'location_name' deve ser uma string.", location_name=v) # ("O campo 'location_name' deve ser uma string.")
        return v.strip().lower()