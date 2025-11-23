# app\schemas\weather_forecast.py
from pydantic import Field
from typing import Annotated
from datetime import datetime

from app.schemas.forecast.forecast_create import ForecastCreate

class ForecastView(ForecastCreate):
    id: int
    updated_at: Annotated[datetime, Field(
        description="Data e hora da última atualização no sistema(UTC)",
        json_schema_extra={"example": "2025-06-12T19:00:00Z"}
    )]
    
    class Config:
        from_attributes = True  # pydantic v2 (no v1: orm_mode = True)