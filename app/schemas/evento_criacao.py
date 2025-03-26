from pydantic import BaseModel, Field
from typing import Annotated, Optional, List
from datetime import datetime

class EventoCriacao(BaseModel):
    title: Annotated[str, Field(max_length=100, description="Título do evento")]
    description: Annotated[str, Field(description="Descrição detalhada")]
    event_date: Annotated[datetime, Field(description="Data e hora do evento")]
    location_name: Annotated[str, Field(description="Nome do local")]
    participants: Annotated[List[str], Field(description="Lista de nomes dos participantes")]
    local_info: Optional[dict] = None
    forecast_info: Optional[dict] = None