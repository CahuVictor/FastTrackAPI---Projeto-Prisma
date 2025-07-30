from pydantic import BaseModel, Field, field_validator
from typing import Annotated
from structlog import get_logger

from app.schemas.venue_type import VenueTypes

logger = get_logger().bind(module="local_info")

class LocalInfo(BaseModel):
    location_name: Annotated[str, Field(description="Nome do local", min_length=2, json_schema_extra={"example":"CESAR"})]
    capacity: Annotated[int, Field(ge=0, description="Capacidade máxima de pessoas", json_schema_extra={"example":150}, default=1)]  # >= 1
    venue_type: Annotated[VenueTypes | None, Field(description="Tipo de local (auditório, salão, etc.)", default=None)]
    is_accessible: Annotated[bool, Field(description="Possui acessibilidade", default=False)]
    address: Annotated[str | None, Field(description="Endereço completo", min_length=5, json_schema_extra={"example":"Rua das Flores, 456"}, default=None)]
    
    @field_validator("location_name", mode="before")
    @classmethod
    def normalizar_nome_local(cls, v):
        if not isinstance(v, str):
            logger.warning("O campo 'location_name' deve ser uma string.", location_name=v)
            raise TypeError("O campo 'location_name' deve ser uma string.")
        return v.strip().lower()

class LocalInfoResponse(LocalInfo):
    manually_edited: bool = Field(default=False, description="Flag indicando se os dados foram alterados manualmente pelo usuário")