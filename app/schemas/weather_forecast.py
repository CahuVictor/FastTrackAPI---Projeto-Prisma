# app\schemas\weather_forecast.py
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime

class ForecastInfo(BaseModel):
    forecast_datetime: Annotated[datetime, Field(description="Data e hora da previsão")]
    temperature: Annotated[float | None, Field(description="Temperatura prevista (°C)")] = None
    weather_main: Annotated[str, Field(description="Condição geral (ex: Clear, Rain)")]
    weather_desc: Annotated[str, Field(description="Descrição detalhada do clima")]
    humidity: Annotated[int, Field(description="Umidade relativa (%)")]
    wind_speed: Annotated[float, Field(description="Velocidade do vento (m/s)")]

class ForecastInfoResponse(ForecastInfo):
    updated_at: Annotated[datetime, Field(
        description="Data e hora da última atualização (UTC)",
        json_schema_extra={"example": "2025-06-12T19:00:00Z"}
    )]