from app.repositories.event_mem import InMemoryEventRepo

# Módulo responsável por manter instâncias únicas manuais (sem usar lru_cache)
_in_memory_repo_instance: InMemoryEventRepo | None = None

def get_in_memory_event_repo() -> InMemoryEventRepo:
    global _in_memory_repo_instance
    if _in_memory_repo_instance is None:
        _in_memory_repo_instance = InMemoryEventRepo()
        if _in_memory_repo_instance is None:
            raise RuntimeError("Repositório em memória não foi inicializado corretamente.")
    return _in_memory_repo_instance
