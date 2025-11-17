from app.infra.repositories.inmemory.event_repo_inmemory import EventRepoInMemory
from app.infra.repositories.inmemory.local_repo_inmemory import LocalRepoInMemory
from app.repositories.user_mem import InMemoryUserRepo

# Módulo responsável por manter instâncias únicas manuais (sem usar lru_cache)
_in_memory_event_repo_instance: EventRepoInMemory | None = None
_in_memory_local_repo_instance: LocalRepoInMemory | None = None
_in_memory_user_repo_instance: InMemoryUserRepo | None = None

def get_in_memory_event_repo() -> EventRepoInMemory:
    global _in_memory_event_repo_instance
    if _in_memory_event_repo_instance is None:
        _in_memory_event_repo_instance = EventRepoInMemory()
        if _in_memory_event_repo_instance is None:
            raise RuntimeError("Repositório em memória não foi inicializado corretamente.")
    return _in_memory_event_repo_instance

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