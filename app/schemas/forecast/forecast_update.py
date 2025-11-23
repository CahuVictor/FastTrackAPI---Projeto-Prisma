# app\schemas\event_update.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from app.models.event_local_enums import VenueType
from datetime import datetime

class ForecastUpdate(BaseModel):
    forecast_datetime: Annotated[datetime | None, Field(description="Data e hora da previsão")] = None
    temperature: Annotated[float | None, Field(description="Temperatura prevista (°C)", json_schema_extra={"example":27.5})] = None
    weather_main: Annotated[str | None, Field(description="Condição geral (ex: Clear, Rain)", json_schema_extra={"example":"Clear"})] = None
    weather_desc: Annotated[str | None, Field(description="Descrição detalhada do clima", json_schema_extra={"example":"Céu limpo com poucas nuvens"})] = None
    humidity: Annotated[int | None, Field(description="Umidade relativa (%)")] = None
    wind_speed: Annotated[float | None, Field(description="Velocidade do vento (m/s)")] = None
    # TODO Adicionar um campo que indique a data de atualização do site
    
    updated_at:  Annotated[datetime, Field(description="Data e hora da última atualização no sistema(UTC)", json_schema_extra={"example": "2025-06-12T19:00:00Z"})]
    
    # ➋  NÃO permita chaves desconhecidas ─ o teste "tipo_invalido" exige 422
    model_config = ConfigDict(extra="forbid")