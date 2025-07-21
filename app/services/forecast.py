# app\services\forecast.py
import asyncio
from structlog import get_logger
from datetime import datetime, timezone, timedelta

from app.services.interfaces.forecast_info_protocol import AbstractForecastService
from app.repositories.event import AbstractEventRepo

from app.deps import provide_forecast_service, provide_event_repo

logger = get_logger().bind(module="forecast")

async def atualizar_forecast_em_background(
    event_id: int,
    retries: int = 3,
    delay: float = 2.0
):
    service: AbstractForecastService = provide_forecast_service()
    repo: AbstractEventRepo = provide_event_repo()
    
    for try_count in range(retries):
        try:
            event = repo.get(event_id)
            if event is None:
                logger.warning("Evento não encontrado durante atualização do forecast", event_id=event_id)
                return
            
            forecast = service.get_by_city_and_datetime(event.city, event.event_date)
            logger.debug("Forecast retornado pelo serviço", event_id=event_id, forecast=forecast)
            
            if forecast is not None:
                from app.schemas.event_update import ForecastInfoUpdate
                from app.utils.patch import update_event
                
                data = forecast.model_dump()
                logger.debug("Dados do forecast antes da validação", event_id=event_id, data=data)

                # Atualiza o timestamp da última atualização bem-sucedida
                data["updated_at"] = datetime.now(timezone.utc)
                update = ForecastInfoUpdate.model_validate(data)
                logger.debug("Dados do forecast após a validação", event_id=event_id, data=data)
                update_event(event, update, attr="forecast_info")
                logger.debug("Atualizando objeto eventos", updated_event=event)
                
                repo.replace_by_id(event_id, event)
                logger.info("Forecast atualizado com sucesso via background", event_id=event_id, updated_at=update.updated_at.isoformat())
            return
        except Exception as e:
            logger.warning(f"Tentativa {try_count + 1} falhou", event_id=event_id, error=str(e))
            await asyncio.sleep(delay)

    logger.error("Falha definitiva ao atualizar previsão do tempo", event_id=event_id)

