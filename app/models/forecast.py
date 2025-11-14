# app/models/forecast.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True, kw_only=True)
class Forecast:
    id: int | None = None
    forecast_datetime: datetime
    temperature: float | None = None
    weather_main: str = ""
    weather_desc: str = ""
    humidity: int = 0
    wind_speed: float = 0.0

    @property
    def is_hot(self) -> bool:
        return (self.temperature or 0.0) >= 30.0

    @classmethod
    def create(
        cls,
        *,
        forecast_datetime: datetime,
        temperature: float | None,
        weather_main: str,
        weather_desc: str,
        humidity: int,
        wind_speed: float,
    ) -> "ForecastInfo":
        return cls(
            id=None,
            forecast_datetime=forecast_datetime,
            temperature=temperature,
            weather_main=weather_main,
            weather_desc=weather_desc,
            humidity=humidity,
            wind_speed=wind_speed,
        )
