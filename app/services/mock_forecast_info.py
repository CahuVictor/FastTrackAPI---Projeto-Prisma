# app/services/mock_forecast_info.py
from datetime import datetime, timedelta
from structlog import get_logger

from app.schemas.weather_forecast import ForecastInfo
from app.services.interfaces.forecast_info_protocol import AbstractForecastService

logger = get_logger().bind(module="mock_forecast_info")

class MockForecastService(AbstractForecastService):
    def get_by_city_and_datetime(self, city: str, date: datetime) -> ForecastInfo | None:
        """
        Gera previsões simuladas a cada 6h para os próximos 10 dias para uma cidade,
        e retorna a previsão mais próxima do datetime solicitado.
        Caso a cidade não exista na lista, retorna None.
        """
        logger.info("Usando serviço de forecast mockado", city=city, date=date)
        # Definições por cidade para variar um pouco
        base_temp = {
            "recife": 28,
            "porto alegre": 21,
            "são paulo": 23,
            "fortaleza": 30,
            "curitiba": 19
        }
        temp_base = base_temp.get(city.lower())  # Não define default, retorna None se não existir
        
        if temp_base is None:
            logger.warning("Cidade não suportada na simulação de previsão", city=city, date=str(date))
            return None

        previsoes = []
        # start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        start = date.replace(hour=0, minute=0)
        for day in range(10):
            for hour in [0, 6, 12, 18]:
                dt = start + timedelta(days=day, hours=hour)
                idx = (day * 4 + hour // 6) % 4
                previsoes.append(
                    ForecastInfo(
                        forecast_datetime=dt,
                        temperature=temp_base + (idx * 2) + (hour / 8),
                        weather_main=["Clear", "Rain", "Clouds", "Thunderstorm"][idx],
                        weather_desc=["Céu limpo", "Chuva leve", "Nuvens dispersas", "Tempestade elétrica"][idx],
                        humidity=65 + idx,
                        wind_speed=2.5 + idx,
                    )
                )
        
        # Compara todas as distâncias em segundos e devolve o objeto ForecastInfo cuja data/hora está mais próxima
        forecast = min(previsoes, key=lambda p: abs((p.forecast_datetime - date).total_seconds()))
        logger.info(
            "Previsão simulada gerada",
            city=city,
            data_solicitada=str(date),
            data_prevista=str(forecast.forecast_datetime),
            condicao=forecast.weather_main
        )
        
        return forecast