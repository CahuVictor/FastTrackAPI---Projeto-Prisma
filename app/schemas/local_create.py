from pydantic import BaseModel, Field, field_validator
from typing import Annotated

from app.models.venue_type import VenueType

class LocalCreate(BaseModel):
    location_name: Annotated[str, Field(description="Nome do local", min_length=2, json_schema_extra={"example":"CESAR"})]
    capacity: Annotated[int, Field(ge=0, description="Capacidade máxima de pessoas", json_schema_extra={"example":150}, default=1)]  # >= 1
    venue_type: Annotated[VenueType | None, Field(description="Tipo de local (auditório, salão, etc.)", default=None)]
    is_accessible: Annotated[bool, Field(description="Possui acessibilidade", default=False)]
    address: Annotated[str | None, Field(description="Endereço completo", min_length=5, json_schema_extra={"example":"Rua das Flores, 456"}, default=None)]
    
    @field_validator("location_name", mode="before")
    @classmethod
    def normalizar_nome_local(cls, v):
        if not isinstance(v, str):
            raise TypeError("O campo 'location_name' deve ser uma string.", location_name=v) # ("O campo 'location_name' deve ser uma string.")
        return v.strip().lower()