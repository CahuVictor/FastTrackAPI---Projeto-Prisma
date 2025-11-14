# app/repositories/evento.py
from __future__ import annotations

import abc

from app.models.event import Event

class EventRepository(abc.ABC):    
    @abc.abstractmethod
    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        city: str | None = None,
        # **filters
    ) -> list[Event]:
        """."""
    
    @abc.abstractmethod
    def get(self, event_id: int) -> Event | None:
        """."""
    
    @abc.abstractmethod
    def add(self, event: Event) -> Event:
        """."""
    
    @abc.abstractmethod
    def replace_all(self, events: list[Event]) -> list[Event]:
        """."""
    
    @abc.abstractmethod
    def replace_by_id(self, event_id: int, event: Event) -> Event:
        """."""
    
    @abc.abstractmethod
    def delete(self) -> None:
        """."""
    
    @abc.abstractmethod
    def delete(self, event_id: int) -> bool:
        """."""
    
    @abc.abstractmethod
    # def update(self, event_id: int, data: dict) -> Event:
    def update(self, event: Event) -> Event:
        """."""
    
