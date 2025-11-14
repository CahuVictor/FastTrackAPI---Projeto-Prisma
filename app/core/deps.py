# app/core/deps.py
from __future__ import annotations

from typing import Generator
from redis.asyncio import Redis
from sqlalchemy.orm import Session
from fastapi import Depends
from structlog import get_logger

from app.infra.db.session import get_db
from app.repositories.event_repo import EventRepository
from app.infra.repositories.sqlalchemy.event_repo_sqlalchemy import EventRepoSQLAlchemy
from app.infra.repositories.inmemory.event_repo_inmemory import EventRepoInMemory

# from app.services.interfaces.user_protocol import AbstractUserRepo
# # from app.services.mock_users import MockUserRepo
# # from app.services.user_db import UserRepo

# # from app.services.local_info_api import LocalInfoService
# from app.services.interfaces.local_info_protocol import AbstractLocalInfoService

# from app.services.mock_forecast_info import MockForecastService
# from app.services.interfaces.forecast_info_protocol import AbstractForecastService

# from app.core.config import get_settings

logger = get_logger().bind(module="deps")

# _settings = get_settings()

# def provide_user_repo(db: Session = Depends(get_db)) -> AbstractUserRepo:
#     """
#     Retorna o repositório de usuários, adaptando à origem de dados.
#     """
#     if _settings.environment == "test.inmemory":
#         from app.core.deps_singletons import get_in_memory_user_repo
#         logger.debug("Injetando instância global de usuários em memória (via singleton manual)")
#         return get_in_memory_user_repo()
#     # logger.debug("Injetando repositório de usuários (SQLAlchemy)")
#     # return UserRepo(db)
#     return get_in_memory_user_repo()

# def provide_local_info_service() -> AbstractLocalInfoService:
#     """
#     Retorna o serviço de localinfo.
#     """
#     if _settings.environment == "test.inmemory":
#         from app.services.mock_local_info import MockLocalInfoService
#         logger.debug("Injetando serviço de local_info (mock)")
#         return MockLocalInfoService()
#     return MockLocalInfoService() # LocalInfoService()

# def provide_forecast_service() -> AbstractForecastService:
#     """
#     Retorna o serviço de forecast.
#     """
#     if _settings.environment == "test.inmemory":
#         logger.debug("Injetando serviço de forecast_info (mock)")
#         return MockForecastService()
#     return MockForecastService()

# _redis_singleton: Redis | None = None     # conexão global reaproveitável

# TODO COLOCAR NO ENV
USE_INMEMORY = True # os.getenv("EVENT_REPO_BACKEND", "sqlalchemy") == "inmemory"

def provide_event_repo(db: Session = Depends(get_db)) -> EventRepository:
    """
    Retorna o repositório de eventos.
    """
    # if _settings.environment == "test.inmemory":
    if USE_INMEMORY:
        from app.core.deps_singletons import get_in_memory_event_repo
        logger.debug("Injetando instância global de repositório em memória (via singleton manual)")
        return get_in_memory_event_repo()
    logger.debug("Injetando repositório de eventos (SQLAlchemy)")
    return EventRepoSQLAlchemy(db)

# async def provide_redis() -> Redis:
#     global _redis_singleton
#     if _settings.redis_url is None:
#         logger.warning("REDIS_URL ausente", environment=_settings.environment)
#         raise RuntimeError("REDIS_URL obrigatório")
#     if _redis_singleton is None:
#         logger.info("Instanciando conexão Redis", url=_settings.redis_url)
#         _redis_singleton = Redis.from_url(
#             _settings.redis_url,
#             decode_responses=True,        # retorna str em vez de bytes
#             health_check_interval=30,     # pool saudável
#         )
#     return _redis_singleton

# def get_db() -> Generator[Session, None, None]:
#     db: Session = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# TODO COLOCAR NO ENV
USE_INMEMORY = True # os.getenv("EVENT_REPO_BACKEND", "sqlalchemy") == "inmemory"

def get_event_repo(db: Session = Depends(get_db)) -> EventRepository:
    """
    Resolve a implementação concreta de EventRepository.

    Se EVENT_REPO_BACKEND=inmemory -> usa repositório em memória.
    Caso contrário -> usa SQLAlchemy.
    """
    if USE_INMEMORY:
        # InMemory não precisa de Session
        return EventRepoInMemory()
    
    return EventRepoSQLAlchemy(db)