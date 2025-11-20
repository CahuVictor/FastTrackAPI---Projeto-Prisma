from app.infra.repositories.inmemory.event_repo_inmemory import EventRepoInMemory
from app.infra.repositories.inmemory.event_audit_repo_inmemory import EventAuditRepoInMemory
from app.infra.repositories.inmemory.local_repo_inmemory import LocalRepoInMemory
from app.infra.repositories.inmemory.user_repo_inmemory import InMemoryUserRepo

# Módulo responsável por manter instâncias únicas manuais (sem usar lru_cache)
_in_memory_event_repo_instance: EventRepoInMemory | None = None
_in_memory_event_audit_repo_instance: EventAuditRepoInMemory | None = None
_in_memory_local_repo_instance: LocalRepoInMemory | None = None
_in_memory_user_repo_instance: InMemoryUserRepo | None = None

def get_in_memory_event_repo() -> EventRepoInMemory:
    global _in_memory_event_repo_instance
    if _in_memory_event_repo_instance is None:
        _in_memory_event_repo_instance = EventRepoInMemory()
        if _in_memory_event_repo_instance is None:
            raise RuntimeError("Repositório em memória não foi inicializado corretamente.")
    return _in_memory_event_repo_instance

def get_in_memory_event_audit_repo() -> EventAuditRepoInMemory:
    """
    Lazily create and return the global in-memory EventAudit repository.

    This mirrors the pattern already used for EventRepoInMemory so that
    the same in-memory instance is reused across requests.
    """
    global _in_memory_event_audit_repo_instance
    if _in_memory_event_audit_repo_instance is None:
        _in_memory_event_audit_repo_instance = EventAuditRepoInMemory()
        if _in_memory_event_audit_repo_instance is None:
            raise RuntimeError("Repositório em memória não foi inicializado corretamente.")
    return _in_memory_event_audit_repo_instance

def get_in_memory_local_repo() -> LocalRepoInMemory:
    global _in_memory_local_repo_instance
    if _in_memory_local_repo_instance is None:
        _in_memory_local_repo_instance = LocalRepoInMemory()
        if _in_memory_local_repo_instance is None:
            raise RuntimeError("Repositório em memória não foi inicializado corretamente.")
    return _in_memory_local_repo_instance

def get_in_memory_user_repo() -> InMemoryUserRepo:
    global _in_memory_user_repo_instance
    if _in_memory_user_repo_instance is None:
        _in_memory_user_repo_instance = InMemoryUserRepo()
        if _in_memory_user_repo_instance is None:
            raise RuntimeError("Repositório em memória não foi inicializado corretamente.")
    return _in_memory_user_repo_instance