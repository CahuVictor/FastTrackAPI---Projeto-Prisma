# app/services/mock_forecast_info.py
from app.schemas.weather_forecast import WeatherForecast
from datetime import datetime, timedelta

def get_mocked_forecast_info(location_name: str, date: datetime) -> list[WeatherForecast]:
    # Simula previsão para 10 dias a partir da data informada, previsão de 6 em 6 horas
    previsoes = []
    for day in range(10):
        for hour in [0, 6, 12, 18]:
            dt = date + timedelta(days=day, hours=hour)
            previsoes.append(
                WeatherForecast(
                    forecast_datetime=dt,
                    temperature=20.0 + (day % 5) + (hour / 6),  # só para variar
                    weather_main=["Clear", "Rain", "Clouds", "Thunderstorm"][day % 4],
                    weather_desc=["Céu limpo", "Chuva leve", "Nuvens dispersas", "Tempestade elétrica"][day % 4],
                    humidity=60 + day,
                    wind_speed=2.0 + (hour / 10)
                )
            )
    return previsoes
