# app/core/deps.py
from __future__ import annotations

from redis.asyncio import Redis
from sqlalchemy.orm import Session
from fastapi import Depends
from structlog import get_logger

from app.infra.db.session import get_db
from app.repositories.auth_session_repo import AuthSessionRepository
from app.repositories.user_repo import UserRepository
from app.repositories.event_repo import EventRepository
from app.repositories.event_audit_repo import EventAuditRepository
from app.repositories.local_repo import LocalRepository
from app.repositories.forecast_repo import ForecastRepository

from app.infra.repositories.sqlalchemy.user_repo_sqlalchemy import UserRepoSQLAlchemy
from app.infra.repositories.sqlalchemy.event_repo_sqlalchemy import EventRepoSQLAlchemy
from app.infra.repositories.sqlalchemy.event_audit_repo_sqlalchemy import EventAuditRepoSQLAlchemy
from app.infra.repositories.inmemory.auth_session_repo_inmemory import AuthSessionRepoInMemory
from app.infra.repositories.inmemory.user_repo_inmemory import UserRepoInMemory
from app.infra.repositories.inmemory.event_repo_inmemory import EventRepoInMemory
from app.infra.repositories.inmemory.event_audit_repo_inmemory import EventAuditRepoInMemory
from app.infra.repositories.inmemory.local_repo_inmemory import LocalRepoInMemory
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.event_service import EventService
from app.services.event_audit_service import EventAuditService
from app.services.local_service import LocalService

# from app.services.interfaces.user_protocol import UserRepository
# # from app.services.mock_users import MockUserRepo
# # from app.services.user_db import UserRepo

# # from app.services.local_info_api import LocalInfoService
# from app.services.interfaces.local_info_protocol import AbstractLocalInfoService

# from app.services.mock_forecast_info import MockForecastService
# from app.services.interfaces.forecast_info_protocol import AbstractForecastService

from app.core.config import get_settings

logger = get_logger().bind(module="deps")

_settings = get_settings()
_redis_singleton: Redis | None = None     # conexão global reaproveitável

def provide_auth_session_repo(
    db: Session = Depends(get_db),
) -> AuthSessionRepository:
    """
    Dependency factory for AuthSessionRepository.

    In test.inmemory environment we use a global in-memory singleton.
    For other environments, you may later plug a SQLAlchemy-based repo.
    
    Rules:
    - If ENVIRONMENT=test.inmemory → use global in-memory singleton repo.
    - Otherwise, a real SQLAlchemy-based implementation should be used
      (not implemented yet, we raise an explicit error for now).
    """
    if _settings.environment == "test.inmemory":
        from app.core.deps_singletons import get_in_memory_auth_session_repo
        logger.debug(
            "Injecting global in-memory AuthSessionRepository (via manual singleton)"
        )
        return get_in_memory_auth_session_repo()

    # TODO: Implement AuthSessionRepoSQLAlchemy when persistence is needed.
    logger.error(
        "AuthSession SQLAlchemy repository not implemented for this environment",
        environment=_settings.environment,
    )
    raise RuntimeError("AuthSession SQL repository not implemented yet")
    logger.debug("AuthSession SQL repository not implemented; using in-memory repo")
    # logger.debug("Injecting SQLAlchemy-based AuthSessionRepository")
    return AuthSessionRepoInMemory()

def provide_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    """
    Dependency factory for the UserRepository abstraction.

    Rules:
    - In `test.inmemory` environment, we inject a global in-memory
      singleton repository (fast tests, no DB required).
    - In all other environments, we inject a SQLAlchemy-based repository.
    """
    if _settings.environment == "test.inmemory":
        from app.core.deps_singletons import get_in_memory_user_repo
        logger.debug("Injecting global in-memory UserRepository (via manual singleton)")
        return get_in_memory_user_repo()
    
    # TODO: create SQLAlchemy-based UserRepository when needed.
    logger.debug("User SQL repository not implemented yet; using in-memory repo")
    # logger.debug("Injecting SQLAlchemy-based UserRepository")
    return None # UserRepoSQLAlchemy(db)

def provide_event_repo(db: Session = Depends(get_db)) -> EventRepository:
    """
    Retorna o repositório de eventos.
    """
    if _settings.environment == "test.inmemory":
        from app.core.deps_singletons import get_in_memory_event_repo
        logger.debug("Injetando instância global de repositório 'Event' em memória (via singleton manual)")
        return get_in_memory_event_repo()
    logger.debug("Injetando repositório Event (SQLAlchemy)")
    return EventRepoSQLAlchemy(db)

def provide_event_audit_repo(db: Session = Depends(get_db)) -> EventAuditRepository:
    """
    Dependency provider for event audit repository.

    Rules:
    - If the current EventRepository is in-memory, we also use an
      in-memory EventAudit repository (global singleton).
    - Otherwise, we create a SQLAlchemy-based EventAudit repository
      using the current DB session.

    This keeps audit storage aligned with how events are being stored
    in the current environment (tests vs production, etc.).
    """
    if _settings.environment == "test.inmemory":
        from app.core.deps_singletons import get_in_memory_event_audit_repo
        logger.debug("Injetando instância global de repositório 'EventAudit' em memória (via singleton manual)")
        return get_in_memory_event_audit_repo()
    logger.debug("Injetando repositório 'EventAudit' (SQLAlchemy)")
    return EventAuditRepoSQLAlchemy(db)

def provide_local_repo(db: Session = Depends(get_db)) -> None: # LocalRepository:
    """
    Retorna o repositório de locais.
    """
    if _settings.environment == "test.inmemory":
        from app.core.deps_singletons import get_in_memory_local_repo
        logger.debug("Injetando instância global de repositório 'Local' em memória (via singleton manual)")
        return get_in_memory_local_repo()
    logger.debug("Injetando repositório Local (SQLAlchemy)")
    return None # EventRepoSQLAlchemy(db)

def provide_forecast_repo(db: Session = Depends(get_db)) -> None: # forecastRepository:
    """
    Retorna o repositório de eventos.
    """
    
    return None

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

def provide_event_service(
    repo: EventRepository = Depends(provide_event_repo),
    audit_repo: EventAuditRepository = Depends(provide_event_audit_repo),
) -> EventService:
    """
    Factory de EventService para injeção de dependência nos controllers.

    Args:
        repo: Implementação de EventRepository (injeção automática).
    
    It wires:
    - the main EventRepository (SQLAlchemy or in-memory);
    - the EventAuditService, which itself uses the chosen audit repository.

    Returns:
        Instância de EventService.
    """
    # return EventService(repo)
    audit_service = EventAuditService(repo=audit_repo)
    service = EventService(repo=repo, audit_service=audit_service)
    
    logger.debug("EventService instance created and wired with audit service")
    return service

def provide_event_audit_service(
    repo: EventRepository = Depends(provide_event_audit_repo),
) -> EventAuditService:
    """
    ???
    """
    return EventAuditService(repo)

def provide_local_service(
    repo: LocalRepository = Depends(provide_local_repo),
) -> LocalService:
    """
    Factory de EventService para injeção de dependência nos controllers.

    Args:
        repo: Implementação de LocalRepository (injeção automática).

    Returns:
        Instância de LocalService.
    """
    return LocalService(repo)

def provide_forecast_service(
    repo: ForecastRepository = Depends(provide_forecast_repo),
) -> None: # ForecastService:
    """
    Factory de EventService para injeção de dependência nos controllers.

    Args:
        repo: Implementação de EventRepository (injeção automática).

    Returns:
        Instância de EventService.
    """
    return None # ForecastService(repo)

def provide_user_service(
    repo: UserRepository = Depends(provide_user_repo),
) -> UserService:
    """
    Factory for UserService instances to be injected into controllers.

    Args:
        repo: Concrete UserRepository implementation chosen by environment.

    Returns:
        Configured UserService instance.
    """
    service = UserService(repo=repo)
    logger.debug("UserService instance created and wired with UserRepository")
    return service

def provide_auth_service(
    user_service: UserService = Depends(provide_user_service),
    session_repo: AuthSessionRepository = Depends(provide_auth_session_repo),
) -> AuthService:
    """
    Factory for AuthService for dependency injection in controllers and utilities.

    Wires:
    - UserService (for user lookup and validation).
    - AuthSessionRepository (for refresh token/session management).
    """
    service = AuthService(
        user_service=user_service,
        session_repo=session_repo,
    )
    logger.debug("AuthService instance created and wired with dependencies")
    return service