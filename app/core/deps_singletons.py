# app/core/deps_singletons.py
from __future__ import annotations

from structlog import get_logger

from app.infra.repositories.inmemory.auth_session_repo_inmemory import AuthSessionRepoInMemory
from app.infra.repositories.inmemory.user_repo_inmemory import UserRepoInMemory
from app.infra.repositories.inmemory.event_repo_inmemory import EventRepoInMemory
from app.infra.repositories.inmemory.audit_repo_inmemory import AuditRepoInMemory
from app.infra.repositories.inmemory.local_repo_inmemory import LocalRepoInMemory

logger = get_logger().bind(module="deps_singletons")

# Módulo responsável por manter instâncias únicas manuais (sem usar lru_cache)
_in_memory_auth_session_repo_instance: AuthSessionRepoInMemory | None = None
_in_memory_user_repo_instance: UserRepoInMemory | None = None
_in_memory_event_repo_instance: EventRepoInMemory | None = None
_in_memory_audit_repo_instance: AuditRepoInMemory | None = None
_in_memory_local_repo_instance: LocalRepoInMemory | None = None

def get_in_memory_auth_session_repo() -> AuthSessionRepoInMemory:
    """
    Return a global singleton instance of the in-memory AuthSessionRepo.
    """
    global _in_memory_auth_session_repo_instance
    if _in_memory_auth_session_repo_instance is None:
        logger.info("Creating global singleton AuthSessionRepoInMemory")
        _in_memory_auth_session_repo_instance = AuthSessionRepoInMemory()
        if _in_memory_auth_session_repo_instance is None:
            raise RuntimeError("Repositório AuthSession em memória não foi inicializado corretamente.")
    return _in_memory_auth_session_repo_instance

def get_in_memory_user_repo() -> UserRepoInMemory:
    """
    Return a global singleton instance of the in-memory UserRepo.
    """
    global _in_memory_user_repo_instance
    if _in_memory_user_repo_instance is None:
        logger.info("Creating global singleton UserRepoInMemory")
        _in_memory_user_repo_instance = UserRepoInMemory()
        if _in_memory_user_repo_instance is None:
            raise RuntimeError("Repositório User em memória não foi inicializado corretamente.")
    return _in_memory_user_repo_instance

def get_in_memory_event_repo() -> EventRepoInMemory:
    global _in_memory_event_repo_instance
    if _in_memory_event_repo_instance is None:
        _in_memory_event_repo_instance = EventRepoInMemory()
        if _in_memory_event_repo_instance is None:
            raise RuntimeError("Repositório Event em memória não foi inicializado corretamente.")
    return _in_memory_event_repo_instance

def get_in_memory_audit_repo() -> AuditRepoInMemory:
    """
    Lazily create and return the global in-memory Audit repository.

    This mirrors the pattern already used for EventRepoInMemory so that
    the same in-memory instance is reused across requests.
    """
    global _in_memory_audit_repo_instance
    if _in_memory_audit_repo_instance is None:
        _in_memory_audit_repo_instance = AuditRepoInMemory()
        if _in_memory_audit_repo_instance is None:
            raise RuntimeError("Repositório Audit em memória não foi inicializado corretamente.")
    return _in_memory_audit_repo_instance

def get_in_memory_local_repo() -> LocalRepoInMemory:
    global _in_memory_local_repo_instance
    if _in_memory_local_repo_instance is None:
        _in_memory_local_repo_instance = LocalRepoInMemory()
        if _in_memory_local_repo_instance is None:
            raise RuntimeError("Repositório Local em memória não foi inicializado corretamente.")
    return _in_memory_local_repo_instance