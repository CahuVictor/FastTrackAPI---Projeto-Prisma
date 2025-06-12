from pydantic import BaseModel, Field, field_validator
from typing import Annotated
from app.schemas.venue_type import VenueTypes

class LocalInfo(BaseModel):
    location_name: Annotated[str, Field(description="Nome do local", min_length=2, json_schema_extra={"example":"CESAR"})]
    capacity: Annotated[int, Field(ge=0, description="Capacidade máxima de pessoas", json_schema_extra={"example":150}, default=1)]  # >= 1
    venue_type: Annotated[VenueTypes | None, Field(description="Tipo de local (auditório, salão, etc.)", default=None)]
    is_accessible: Annotated[bool, Field(description="Possui acessibilidade", default=False)]
    address: Annotated[str | None, Field(description="Endereço completo", min_length=5, json_schema_extra={"example":"Rua das Flores, 456"}, default=None)]
    past_events: Annotated[list[str], Field(description="Histórico de eventos realizados", default_factory=list)]
    manually_edited: bool = Field(default=False, description="Flag indicando se os dados foram alterados manualmente pelo usuário")
    
    @field_validator("location_name", mode="before")
    @classmethod
    def normalizar_nome_local(cls, v):
        if not isinstance(v, str):
            raise TypeError("O campo 'location_name' deve ser uma string.")
        return v.strip().lower()

    @field_validator("past_events", mode="before")
    @classmethod
    def limpar_eventos_passados(cls, v):
        if not isinstance(v, list):
            raise TypeError("O campo 'past_events' deve ser uma lista de strings.")
        if not all(isinstance(item, str) for item in v):
            raise ValueError("Todos os itens em 'past_events' devem ser strings.")
        return [evento.strip() for evento in v]