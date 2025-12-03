# app\schemas\local_create.py
from pydantic import BaseModel, Field, field_validator
from typing import Annotated

from app.models.enums import VenueType
from app.models.local import LocalSource

class LocalCreate(BaseModel):
    name: Annotated[str, Field(description="Nome do local", min_length=2, json_schema_extra={"example":"CESAR"})]
    capacity: Annotated[int, Field(ge=0, description="Capacidade máxima de pessoas", json_schema_extra={"example":150}, default=1)]  # >= 1
    is_accessible: Annotated[bool, Field(description="Possui acessibilidade", default=False)]
    parking_available: Annotated[bool, Field(description="Possui esatcionamento", default=False)]
    
    # Address Block
    address_street: Annotated[str | None, Field(description="Endereço completo", min_length=5, json_schema_extra={"example":"Rua das Flores, 456"}, default=None)]
    address_city: Annotated[str | None, Field(description="Cidade", min_length=5, json_schema_extra={"example":"Recife"}, default=None)]
    address_state: Annotated[str | None, Field(description="Estado", min_length=5, json_schema_extra={"example":"Pernambuco"}, default=None)]
    
    # geo & timezone
    latitude: Annotated[float | None, Field(None, description="Latitude coordinate in decimal degrees")]
    longitude: Annotated[float | None, Field(None, description="Longitude coordinate in decimal degrees")]
    timezone: Annotated[str | None, Field(None, description="IANA timezone for the venue (e.g. 'America/Recife')")]
    
    # integration and origin metadata
    external_id: Annotated[str | None, Field(None, description="Identifier of this local in the external LocalInfo system")]
    source: Annotated[LocalSource | None, Field(None,
        description=(
            "Origin of this Local. If omitted, INTERNAL_SYNC will be used when "
            "coming from sync and MANUAL when created via this API."
        ),
    )]
    
    # physical characteristics
    is_indoor: Annotated[bool | None, Field(None, description="True if venue is indoors")]
    has_cover: Annotated[bool | None, Field(None, description="True if the area is covered")]
    capacity_seated: Annotated[int | None, Field(None, description="Maximum seated capacity")]
    capacity_standing: Annotated[int | None, Field(None, description="Maximum standing capacity")]
    
    contact_phone: Annotated[str | None, Field(description="Tlefone", min_length=5, json_schema_extra={"example":"(81) 9 8765 4321)"}, default=None)]
    images: Annotated[list[str] | None, Field(description="Caminhos das imagens", min_length=5, default=list)]
    
    venue_type: Annotated[VenueType | None, Field(description="Tipo de local (auditório, salão, etc.)", default=None)]
    
    @field_validator("name", mode="before")
    @classmethod
    def normalizar_nome_local(cls, v):
        if not isinstance(v, str):
            raise TypeError("O campo 'name' deve ser uma string.", name=v)
        return v.strip().lower()