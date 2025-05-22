# app/services/mock_forecast_info.py
from app.schemas.weather_forecast import WeatherForecast
from datetime import datetime, timedelta

def get_mocked_forecast_info(city: str, date: datetime) -> WeatherForecast | None:
    """
    Gera previsões simuladas a cada 6h para os próximos 10 dias para uma cidade,
    e retorna a previsão mais próxima do datetime solicitado.
    """
    # Definições por cidade para variar um pouco
    base_temp = {
        "recife": 28,
        "porto alegre": 21,
        "são paulo": 23,
        "fortaleza": 30,
        "curitiba": 19
    }
    temp_base = base_temp.get(city.lower(), 25)  # valor default se cidade não estiver listada

    previsoes = []
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    for day in range(10):
        for hour in [0, 6, 12, 18]:
            dt = start + timedelta(days=day, hours=hour)
            idx = (day * 4 + hour // 6) % 4  # para variar entre os tipos
            previsoes.append(
                WeatherForecast(
                    forecast_datetime=dt,
                    temperature=temp_base + (idx * 2) + (hour / 8),
                    weather_main=["Clear", "Rain", "Clouds", "Thunderstorm"][idx],
                    weather_desc=["Céu limpo", "Chuva leve", "Nuvens dispersas", "Tempestade elétrica"][idx],
                    humidity=65 + (idx * 3) + (day % 4),
                    wind_speed=2.5 + idx * 0.7 + (hour / 24)
                )
            )
    # Encontre a previsão mais próxima da data/hora informada
    previsao_mais_proxima = min(previsoes, key=lambda p: abs((p.forecast_datetime - date).total_seconds()))
    return previsao_mais_proxima
