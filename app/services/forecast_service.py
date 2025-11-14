# app\services\forecast_service.py
import httpx
from datetime import datetime
from typing import List
from structlog import get_logger

from app.models.forecast import Forecast
from app.repositories.forecast_repo import ForecastRepository
from app.schemas.forecast_create import ForecastCreate
from app.schemas.forecast_update import ForecastUpdate

from app.core.deps import provide_forecast_service, provide_event_repo

logger = get_logger().bind(module="forecast")

class ForecastService:
    """
    Implementação real que consulta a API externa de LocalInfo.
    """

    async def get_info_by_coordinates(self, lat: float, lon: float) -> None: # Local:
        # base_url = get_service_url("local_info_url")
        # url = f"{base_url}/local_info?lat={lat}&lon={lon}"

        # async with httpx.AsyncClient() as client:
        #     response = await client.get(url, timeout=10)
        #     response.raise_for_status()
        #     data = response.json()

        # return Local(**data)
        return None


# async def atualizar_forecast_em_background(
#     event_id: int,
#     retries: int = 3,
#     delay: float = 2.0
# ):
#     service: AbstractForecastService = provide_forecast_service()
#     repo: AbstractEventRepo = provide_event_repo()
    
#     for try_count in range(retries):
#         try:
#             event = repo.get(event_id)
#             if event is None:
#                 logger.warning("Evento não encontrado durante atualização do forecast", event_id=event_id)
#                 return
            
#             forecast = service.get_by_city_and_datetime(event.city, event.event_date)
#             logger.debug("Forecast retornado pelo serviço", event_id=event_id, forecast=forecast)
            
#             if forecast is not None:
#                 from app.schemas.event_update import ForecastInfoUpdate
#                 from app.utils.patch import update_event
                
#                 data = forecast.model_dump()
#                 logger.debug("Dados do forecast antes da validação", event_id=event_id, data=data)

#                 # Atualiza o timestamp da última atualização bem-sucedida
#                 data["updated_at"] = datetime.now(timezone.utc)
#                 update = ForecastInfoUpdate.model_validate(data)
#                 logger.debug("Dados do forecast após a validação", event_id=event_id, data=data)
#                 update_event(event, update, attr="forecast_info")
#                 logger.debug("Atualizando objeto eventos", updated_event=event)
                
#                 repo.replace_by_id(event_id, event)
#                 logger.info("Forecast atualizado com sucesso via background", event_id=event_id, updated_at=update.updated_at.isoformat())
#             return
#         except Exception as e:
#             logger.warning(f"Tentativa {try_count + 1} falhou", event_id=event_id, error=str(e))
#             await asyncio.sleep(delay)

#     logger.error("Falha definitiva ao atualizar previsão do tempo", event_id=event_id)

