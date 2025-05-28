# app/deps.py
from app.services.interfaces.user import AbstractUserRepo
from app.services.mock_users import MockUserRepo

from app.services.mock_local_info import MockLocalInfoService
from app.services.interfaces.local_info import AbstractLocalInfoService

from app.services.mock_forecast_info import MockForecastService
from app.services.interfaces.forecast_info import AbstractForecastService

def provide_user_repo() -> AbstractUserRepo:
    return MockUserRepo()

def provide_local_info_service() -> AbstractLocalInfoService:
    return MockLocalInfoService()

def provide_forecast_service() -> AbstractForecastService:
    return MockForecastService()