# app/repositories/evento.py
import abc
from app.schemas.event_create import EventCreate
from app.schemas.event_create import EventResponse
from app.schemas.weather_forecast import WeatherForecast

class AbstractEventRepo(abc.ABC):
    @abc.abstractmethod
    def list_all(self) -> list[EventResponse]:
        """."""
    
    # @abc.abstractmethod
    # def list_partial(
    #     self,
    #     *,
    #     skip: int = 0,
    #     limit: int = 20,
    #     city: str | None = None,
    # ) -> list[EventResponse]:
    #     """."""
    
    @abc.abstractmethod
    def list_partial(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        **filters
    ) -> list[EventResponse]:
        """."""
    
    @abc.abstractmethod
    def get(self, evento_id: int) -> EventResponse | None:
        """."""
    
    @abc.abstractmethod
    def add(self, evento: EventCreate, forecast_info: WeatherForecast | None = None) -> EventResponse:
        """."""
    
    @abc.abstractmethod
    def replace_all(self, eventos: list[EventResponse]) -> list[EventResponse]:
        """."""
    
    @abc.abstractmethod
    def replace_by_id(self, evento_id: int, evento: EventResponse) -> EventResponse:
        """."""
    
    @abc.abstractmethod
    def delete_all(self) -> None:
        """."""
    
    @abc.abstractmethod
    def delete_by_id(self, evento_id: int) -> bool:
        """."""
    
    @abc.abstractmethod
    def update(self, evento_id: int, data: dict) -> EventResponse:
        """."""
    
