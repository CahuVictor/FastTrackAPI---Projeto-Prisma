# app/deps.py
from app.services.interfaces.user import AbstractUserRepo
from app.services.mock_users import MockUserRepo

from app.services.mock_local_info import MockLocalInfoService
from app.services.interfaces.local_info import AbstractLocalInfoService

from app.services.mock_forecast_info import MockForecastService
from app.services.interfaces.forecast_info import AbstractForecastService

from app.repositories.evento import AbstractEventoRepo

from functools import lru_cache
from app.repositories.evento_mem import InMemoryEventoRepo

def provide_user_repo() -> AbstractUserRepo:
    return MockUserRepo()

def provide_local_info_service() -> AbstractLocalInfoService:
    return MockLocalInfoService()

def provide_forecast_service() -> AbstractForecastService:
    return MockForecastService()

# def provide_evento_repo() -> AbstractEventoRepo:
#     return InMemoryEventoRepo()

# uma instância global
_evento_repo_singleton = InMemoryEventoRepo()

def provide_evento_repo() -> InMemoryEventoRepo:
    """
    Retorna sempre a mesma instância em memória para toda a aplicação/testes.
    """
    return _evento_repo_singleton