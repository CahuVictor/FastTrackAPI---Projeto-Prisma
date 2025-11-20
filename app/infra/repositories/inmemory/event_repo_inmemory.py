# app/infra/repositories/inmemory/event_repo_inmemory.py
from __future__ import annotations

from structlog import get_logger
from typing import Dict, List
from datetime import datetime

from app.models.event import Event
from app.repositories.event_repo import EventRepository

logger = get_logger().bind(module="event_repo_inmemory")

class EventRepoInMemory(): # EventRepository): # TODO TypeError: Can't instantiate abstract class EventRepoInMemory without an implementation for abstract methods 'replace_all', 'replace_by_id'
    """
    In-memory implementation of EventRepository.

    This repository is meant for:
    - Unit tests.
    - Development environments without a real database.
    - Quick prototypes and experiments.

    It keeps behavior aligned with the SQLAlchemy version:
    - Auto-generates `id`.
    - Sets `created_at` when inserting.
    - Updates `updated_at` when modifying.
    """
    
    def __init__(self):
        """
        Initializes an empty in-memory store and an ID counter.
        """
        self._storage: Dict[int, Event] = {}
        self._next_id: int = 1

        logger.debug("EventRepoInMemory initialized")
    
    def _generate_id(self) -> int:
        """
        Generates a new incremental ID for in-memory events.

        Returns:
            New integer ID.
        """
        new_id = self._next_id
        self._next_id += 1
        return new_id
    
    # ----------------------------------------------------------------------
    # CREATE
    # ----------------------------------------------------------------------
    def add(self, event: Event) -> Event:
        """
        Adds a new Event to the in-memory store.

        If `event.id` is None, an incremental ID is assigned.
        `created_at` and `updated_at` are set to the current UTC time.

        Args:
            event: Domain Event entity to be stored.

        Returns:
            The same Event entity with `id`, `created_at` and `updated_at` populated.
        """
        if event.id is None:
            event.id = self._generate_id()
        
        now = datetime.utcnow()
        event.created_at = now
        event.updated_at = now
        
        self._storage[event.id] = event
        
        logger.info(
            "Evento adicionado em memória",
            event_id=event.id,
            title=event.title,
            city=event.city,
            status=event.status,
            start_time=event.start_time,
        )

        return event
    
    # ----------------------------------------------------------------------
    # READ
    # ----------------------------------------------------------------------
    def get(self, event_id: int) -> Event | None:
        """
        Retrieves an Event from the in-memory store by its ID.

        Args:
            event_id: Identifier of the event to be retrieved.

        Returns:
            The Event if found, or None if it does not exist.
        """
        event = self._storage.get(event_id)
        
        if event:
            logger.info(
                "Evento encontrado em memória",
                event_id=event_id,
                title=event.title,
                city=event.city,
                status=event.status,
                start_time=event.start_time,
            )
        else:
            logger.info("Evento não encontrado em memória", event_id=event_id)

        return event

    # ----------------------------------------------------------------------
    # LIST
    # ----------------------------------------------------------------------
    def list(self, *, skip: int = 0, limit: int = 20, city: str | None = None, **filters) -> list[Event]:
        """
        Returns a paginated slice of events with optional filters.

        Events are sorted by `event_date` in descending order.

        Args:
            skip: Number of records to skip from the beginning.
            limit: Maximum number of records to return; if <= 0, no limit is applied.
            city: If provided, filters events whose `city` matches exactly.
            **filters: Reserved for future dynamic filtering support.

        Returns:
            A list of Event entities matching the filter and pagination.
        """
        events = list(self._storage.values())
        
        if city:
            events = [e for e in events if e.city == city]

        events.sort(key=lambda e: e.start_time, reverse=True)

        if skip:
            events = events[skip:]

        if limit > 0:
            events = events[:limit]

        logger.info(
            "Listando eventos em memória",
            total=len(events),
            skip=skip,
            limit=limit,
            city=city,
        )

        return events
    
    # ----------------------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------------------
    def update(self, event: Event) -> Event:
        """
        Updates an existing Event in the in-memory store.

        `updated_at` is automatically refreshed to the current UTC time.

        Args:
            event: Event entity containing the new state. It must have a valid `id`.

        Returns:
            The updated Event entity.

        Raises:
            ValueError: If `event.id` is None.
            KeyError: If no record exists for the informed `id`.
        """
        if event.id is None:
            logger.error("Tentativa de update em memória sem id", event=event)
            raise ValueError("Cannot update Event without id")

        if event.id not in self._storage:
            logger.warning("Evento não encontrado em memória para update", event_id=event.id)
            raise KeyError("Event not found")
        
        # atualiza updated_at
        event.updated_at = datetime.utcnow()

        self._storage[event.id] = event

        logger.info(
            "Evento atualizado em memória",
            event_id=event.id,
            title=event.title,
            city=event.city,
            status=event.status,
            start_time=event.start_time,
            updated=event.updated_at,
        )

        return event

    # def replace_all(self, events: list[EventResponse]) -> list[EventResponse]:
    #     self._db = {e.id: e for e in events}
    #     logger.info("Todos os eventos foram substituídos", total=len(events))
    #     return list(self._db.values())

    # def delete_all(self) -> None:
    #     """Remove todos os eventos e zera o contador de IDs (usado em testes)."""
    #     self._db.clear()
    #     self._id_counter = 1
    #     logger.info("Todos os eventos foram deletados")

    # ----------------------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------------------
    def delete(self, event_id: int) -> bool:
        """
        Removes an Event from the in-memory store, if it exists.

        Args:
            event_id: Identifier of the event to be removed.

        Returns:
            True if the event was removed, False if it did not exist.
        """
        if event_id in self._storage:
            del self._storage[event_id]
            logger.info("Evento removido em memória", event_id=event_id)
            return True
        logger.info(
            "Tentativa de remover evento inexistente em memória",
            event_id=event_id,
        )
        return False