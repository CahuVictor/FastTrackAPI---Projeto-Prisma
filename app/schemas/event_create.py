from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
from app.schemas.weather_forecast import WeatherForecast
from app.schemas.local_info import LocalInfo

from pydantic import field_validator

class EventCreate(BaseModel):
    @field_validator("title", "description", mode="before")
    @classmethod
    def limpar_texto(cls, v):
        return v.strip().title() if isinstance(v, str) else v

    # @field_validator("location_name", mode="before")
    # @classmethod
    # def normalizar_nome_local(cls, v):
    #     return v.strip().lower() if isinstance(v, str) else v

    # id: int | None = None
    title: Annotated[str, Field(max_length=100, description="Título do evento", json_schema_extra={"example": "Festival de Tecnologia"})]
    description: Annotated[str, Field(description="Descrição detalhada", json_schema_extra={"example": "Evento com oficinas, palestras e música."})]
    event_date: Annotated[datetime, Field(description="Data e hora do evento", json_schema_extra={"example": "2025-06-12T19:00:00"})]
    # location_name: Annotated[str, Field(description="Nome do local", json_schema_extra={"example": "Auditório Central")] # Removido por redundância em local_info
    participants: Annotated[list[str], Field(description="Lista de participantes", json_schema_extra={"example": ["Alice", "Bob", "Carol"]})]
    # local_info: LocalInfo | None = None # obsoleto Optional[dict]
    local_info: LocalInfo
    forecast_info: WeatherForecast | None = None
    
class EventResponse(EventCreate):
    id: int