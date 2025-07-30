# app/services/interfaces/forecast_info.py
from datetime import datetime
from app.schemas.weather_forecast import ForecastInfo
from typing import Protocol

class AbstractForecastService(Protocol):
    def get_by_city_and_datetime(self, city: str, date: datetime) -> ForecastInfo | None: ...
