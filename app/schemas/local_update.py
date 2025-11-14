# app\schemas\event_update.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from app.models.venue_type import VenueType
from datetime import datetime

class LocalUpdate(BaseModel):
    location_name: Annotated[str | None, Field(description="Nome do local", min_length=2, json_schema_extra={"example":"Empresa XYZ"})] = None
    capacity: Annotated[int | None, Field(ge=0, json_schema_extra={"example":100}, description="Capacidade máxima de pessoas")] = None
    venue_type: Annotated[VenueType | None, Field(description="Tipo de local (auditório, salão, etc.)")] = None
    is_accessible: Annotated[bool | None, Field(description="Possui acessibilidade", json_schema_extra={"example":False})] = None
    address: Annotated[str | None, Field(min_length=5, json_schema_extra={"example":"Rua Atualizada, 123"}, description="Endereço completo")] = None
    # past_events: Annotated[list[str] | None, Field(description="Histórico de eventos realizados", json_schema_extra={"example":["Evento A", "Evento B"]})] = None
    manually_edited: Annotated[bool, Field(description="Flag indicando se os dados foram alterados manualmente pelo usuário", default=False, json_schema_extra={"example":False})]
    
    # ➋  NÃO permita chaves desconhecidas ─ o teste "tipo_invalido" exige 422
    model_config = ConfigDict(extra="forbid")