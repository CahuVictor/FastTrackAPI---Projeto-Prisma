# app/repositories/evento.py
from typing import Protocol
from app.schemas.event_create import EventCreate
from app.schemas.event_create import EventResponse

class AbstractEventRepo(Protocol):
    def list_all(self) -> list[EventResponse]: ...
    
    # def list_partial(
    #     self,
    #     *,
    #     skip: int = 0,
    #     limit: int = 20,
    #     city: str | None = None,
    # ) -> list[EventResponse]: ...
    
    def list_partial(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        **filters
    ) -> list[EventResponse]: ...
    
    def get(self, evento_id: int) -> EventResponse | None: ...
    
    def add(self, evento: EventCreate) -> EventResponse: ...
    
    def replace_all(self, eventos: list[EventResponse]) -> list[EventResponse]: ...
    
    def replace_by_id(self, evento_id: int, evento: EventResponse) -> EventResponse: ...
    
    def delete_all(self) -> None: ...
    
    def delete_by_id(self, evento_id: int) -> bool: ...
    
    def update(self, evento_id: int, data: dict) -> EventResponse: ...
    
