from pydantic import BaseModel, Field
from typing import Annotated, List

class LocalInfo(BaseModel):
    location_name: Annotated[str, Field(description="Nome do local")]
    capacity: Annotated[int, Field(ge=0, description="Capacidade máxima de pessoas")]
    venue_type: Annotated[str, Field(description="Tipo de local (auditório, salão, etc.)")]
    is_accessible: Annotated[bool, Field(description="Possui acessibilidade")]
    address: Annotated[str, Field(description="Endereço completo")]
    past_events: Annotated[List[str], Field(description="Histórico de eventos realizados")]