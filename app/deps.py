# app/deps.py
from redis.asyncio import Redis
from structlog import get_logger
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.session import get_db

from app.repositories.event_orm_db import SQLEventRepo
from app.repositories.event import AbstractEventRepo
# from app.repositories.user import AbstractUserRepo

from app.services.interfaces.user_protocol import AbstractUserRepo
# from app.services.mock_users import MockUserRepo
# from app.services.user_db import UserRepo

# from app.services.local_info_api import LocalInfoService
from app.services.interfaces.local_info_protocol import AbstractLocalInfoService

from app.services.mock_forecast_info import MockForecastService
from app.services.interfaces.forecast_info_protocol import AbstractForecastService

from app.core.config import get_settings

logger = get_logger().bind(module="deps")

_settings = get_settings()

def provide_user_repo(db: Session = Depends(get_db)) -> AbstractUserRepo:
    """
    Retorna o repositório de usuários, adaptando à origem de dados.
    """
    if _settings.environment == "test.inmemory":
        from app.deps_singletons import get_in_memory_user_repo
        logger.debug("Injetando instância global de usuários em memória (via singleton manual)")
        return get_in_memory_user_repo()
    # logger.debug("Injetando repositório de usuários (SQLAlchemy)")
    # return UserRepo(db)
    return get_in_memory_user_repo()

def provide_local_info_service() -> AbstractLocalInfoService:
    """
    Retorna o serviço de localinfo.
    """
    if _settings.environment == "test.inmemory":
        from app.services.mock_local_info import MockLocalInfoService
        logger.debug("Injetando serviço de local_info (mock)")
        return MockLocalInfoService()
    return MockLocalInfoService() # LocalInfoService()

def provide_forecast_service() -> AbstractForecastService:
    """
    Retorna o serviço de forecast.
    """
    if _settings.environment == "test.inmemory":
        logger.debug("Injetando serviço de forecast_info (mock)")
        return MockForecastService()
    return MockForecastService()

_redis_singleton: Redis | None = None     # conexão global reaproveitável

def provide_event_repo(db: Session = Depends(get_db)) -> AbstractEventRepo:
    """
    Retorna o repositório de eventos.
    """
    if _settings.environment == "test.inmemory":
        from app.deps_singletons import get_in_memory_event_repo
        logger.debug("Injetando instância global de repositório em memória (via singleton manual)")
        return get_in_memory_event_repo()
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