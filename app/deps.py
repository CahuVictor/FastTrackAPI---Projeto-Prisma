# app/deps.py
from redis.asyncio import Redis
from structlog import get_logger
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.session import get_db
from app.repositories.event_orm_db import SQLEventRepo
from app.repositories.event import AbstractEventRepo

from app.services.interfaces.user_protocol import AbstractUserRepo
from app.services.mock_users import MockUserRepo

from app.services.mock_local_info import MockLocalInfoService
from app.services.interfaces.local_info_protocol import AbstractLocalInfoService

from app.services.mock_forecast_info import MockForecastService
from app.services.interfaces.forecast_info_protocol import AbstractForecastService

# from app.repositories.event import AbstractEventRepo

# from functools import lru_cache
from app.repositories.event_mem import InMemoryEventRepo

from app.core.config import get_settings

logger = get_logger().bind(module="deps")

_settings = get_settings()

def provide_user_repo() -> AbstractUserRepo:
    logger.debug("Injetando repositório de usuários (mock)")
    return MockUserRepo()

def provide_local_info_service() -> AbstractLocalInfoService:
    logger.debug("Injetando serviço de local_info (mock)")
    return MockLocalInfoService()

def provide_forecast_service() -> AbstractForecastService:
    logger.debug("Injetando serviço de forecast_info (mock)")
    return MockForecastService()

# def provide_event_repo() -> AbstractEventRepo:
#     return InMemoryEventRepo()

# uma instância global
# _evento_repo_singleton = InMemoryEventRepo()

_redis_singleton: Redis | None = None     # conexão global reaproveitável

# def provide_event_repo() -> InMemoryEventRepo:
#     """
#     Retorna sempre a mesma instância em memória para toda a aplicação/testes.
#     """
#     logger.debug("Injetando repositório de eventos (singleton)")
#     return _evento_repo_singleton

def provide_event_repo(db: Session = Depends(get_db)) -> AbstractEventRepo:
    logger.debug("Injetando repositório de eventos (SQLAlchemy)")
    return SQLEventRepo(db)

async def provide_redis() -> Redis:
    global _redis_singleton
    if _settings.redis_url is None:
        logger.warning("REDIS_URL ausente", environment=_settings.environment)
        raise RuntimeError("REDIS_URL obrigatório")
    if _redis_singleton is None:
        logger.info("Instanciando conexão Redis", url=_settings.redis_url)
        _redis_singleton = Redis.from_url(
            _settings.redis_url,
            decode_responses=True,        # retorna str em vez de bytes
            health_check_interval=30,     # pool saudável
        )
    return _redis_singleton