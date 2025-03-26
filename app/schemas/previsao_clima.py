from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime

class PrevisaoClima(BaseModel):
    forecast_datetime: Annotated[datetime, Field(description="Data e hora da previsão")]
    temperature: Annotated[float, Field(description="Temperatura prevista (°C)")]
    weather_main: Annotated[str, Field(description="Condição geral (ex: Clear, Rain)")]
    weather_desc: Annotated[str, Field(description="Descrição detalhada do clima")]
    humidity: Annotated[int, Field(description="Umidade relativa (%)")]
    wind_speed: Annotated[float, Field(description="Velocidade do vento (m/s)")]