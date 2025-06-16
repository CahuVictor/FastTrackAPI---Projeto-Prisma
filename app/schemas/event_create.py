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

    title: Annotated[str, Field(max_length=100, description="Título do evento", json_schema_extra={"example": "Festival de Tecnologia"})]
    description: Annotated[str, Field(description="Descrição detalhada", json_schema_extra={"example": "Evento com oficinas, palestras e música."})]
    event_date: Annotated[datetime, Field(description="Data e hora do evento", json_schema_extra={"example": "2025-06-12T19:00:00"})]
    city: Annotated[str, Field(description="Cidade onde o evento ocorrerá", json_schema_extra={"example": "Recife"})]
    participants: Annotated[list[str], Field(description="Lista de participantes", json_schema_extra={"example": ["Alice", "Bob", "Carol"]})]
    local_info: LocalInfo               # local_info: LocalInfo | None = None # obsoleto Optional[dict]
    
class EventResponse(EventCreate):
    id: int
    forecast_info: WeatherForecast | None = None
    views: int = 0 # (default = 0)
    