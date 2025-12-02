# app/infra/repositories/inmemory/event_repo_inmemory.py
from __future__ import annotations

from structlog import get_logger
from typing import Dict, List
from datetime import datetime

from app.models.event import Event
from app.models.event_filters import EventFilterCriteria
from app.repositories.event_repo import EventRepository

logger = get_logger().bind(module="event_repo_inmemory")


def _apply_filter_and_sort(
    events_list: list[Event],
    *,
    filter: EventFilterCriteria,
) -> list[Event]:
    """
    Apply the in-memory filtering and sorting logic over a list of Events.

    This helper keeps the `list` method smaller and centralizes all
    filter conditions in one place. It also documents the fact that,
    in this in-memory implementation, all data is loaded into memory
    before applying filters — which is different from a future SQL
    implementation, where filters should be translated to WHERE clauses.
    """

    # -------------------------
    # Core content filters
    # -------------------------
    if filter.title is not None:
        if isinstance(filter.title, list):
            needles = [t.lower() for t in filter.title]
            events_list = [
                e
                for e in events_list
                if any(n in e.title.lower() for n in needles)
            ]
        else:
            needle = filter.title.lower()
            events_list = [e for e in events_list if needle in e.title.lower()]

    if filter.description is not None:
        if isinstance(filter.description, list):
            needles = [d.lower() for d in filter.description]
            events_list = [
                e
                for e in events_list
                if any(
                    n in (e.description or "").lower()
                    for n in needles
                )
            ]
        else:
            needle = filter.description.lower()
            events_list = [
                e
                for e in events_list
                if e.description and needle in e.description.lower()
            ]

    if filter.status is not None:
        if isinstance(filter.status, list):
            allowed = set(filter.status)
            events_list = [e for e in events_list if e.status in allowed]
        else:
            events_list = [e for e in events_list if e.status == filter.status]

    # -------------------------
    # Scheduling filters
    # -------------------------
    if filter.start_from is not None:
        events_list = [
            e for e in events_list if e.start_time >= filter.start_from
        ]

    if filter.start_to is not None:
        events_list = [
            e for e in events_list if e.start_time <= filter.start_to
        ]

    # -------------------------
    # Context / classification
    # -------------------------
    if filter.city is not None:
        needle = filter.city.lower()
        events_list = [
            e
            for e in events_list
            if e.city is not None and needle in e.city.lower()
        ]

    if filter.age_restriction is not None:
        if isinstance(filter.age_restriction, list):
            allowed = {a.lower() for a in filter.age_restriction}
            events_list = [
                e
                for e in events_list
                if e.age_restriction and e.age_restriction.lower() in allowed
            ]
        else:
            needle = filter.age_restriction.lower()
            events_list = [
                e
                for e in events_list
                if e.age_restriction and e.age_restriction.lower() == needle
            ]

    if filter.expected_audience is not None:
        events_list = [
            e
            for e in events_list
            if e.expected_audience == filter.expected_audience
        ]

    if filter.environment is not None:
        if isinstance(filter.environment, list):
            allowed = set(filter.environment)
            events_list = [e for e in events_list if e.environment in allowed]
        else:
            events_list = [
                e for e in events_list if e.environment == filter.environment
            ]

    # -------------------------
    # Engagement filters
    # -------------------------
    if filter.participants is not None:
        if isinstance(filter.participants, list):
            needles = [p.lower() for p in filter.participants]
            events_list = [
                e
                for e in events_list
                if any(
                    p.lower() in [ep.lower() for ep in e.participants]
                    for p in needles
                )
            ]
        else:
            needle = filter.participants.lower()
            events_list = [
                e
                for e in events_list
                if any(needle == p.lower() for p in e.participants)
            ]

    if filter.views_min is not None:
        events_list = [
            e for e in events_list if e.views >= filter.views_min
        ]

    if filter.views_max is not None:
        events_list = [
            e for e in events_list if e.views <= filter.views_max
        ]

    # -------------------------
    # Audit filters
    # -------------------------
    if filter.created_from is not None:
        events_list = [
            e
            for e in events_list
            if e.created_at is not None and e.created_at >= filter.created_from
        ]

    if filter.created_to is not None:
        events_list = [
            e
            for e in events_list
            if e.created_at is not None and e.created_at <= filter.created_to
        ]

    if filter.updated_from is not None:
        events_list = [
            e
            for e in events_list
            if e.updated_at is not None and e.updated_at >= filter.updated_from
        ]

    if filter.updated_to is not None:
        events_list = [
            e
            for e in events_list
            if e.updated_at is not None and e.updated_at <= filter.updated_to
        ]

    if filter.deleted_from is not None:
        events_list = [
            e
            for e in events_list
            if e.deleted_at is not None and e.deleted_at >= filter.deleted_from
        ]

    if filter.deleted_to is not None:
        events_list = [
            e
            for e in events_list
            if e.deleted_at is not None and e.deleted_at <= filter.deleted_to
        ]

    # created_by / updated_by / deleted_by como igualdade simples ou lista
    def _match_str_field(value: str | None, criterion: list[str] | str | None) -> bool:
        if criterion is None:
            return True
        if value is None:
            return False
        if isinstance(criterion, list):
            allowed = {c.lower() for c in criterion}
            return value.lower() in allowed
        return value.lower() == criterion.lower()

    events_list = [
        e
        for e in events_list
        if _match_str_field(e.created_by, filter.created_by)
    ]
    events_list = [
        e
        for e in events_list
        if _match_str_field(e.updated_by, filter.updated_by)
    ]
    events_list = [
        e
        for e in events_list
        if _match_str_field(e.deleted_by, filter.deleted_by)
    ]

    # -------------------------
    # Sorting & pagination
    # -------------------------
    # Deterministic ordering: by start_time then id
    events_list.sort(key=lambda e: (e.start_time, e.id or 0))

    # Pagination
    if filter.skip:
        events_list = events_list[filter.skip :]

    if filter.limit and filter.limit > 0:
        events_list = events_list[: filter.limit]

    return events_list


class EventRepoInMemory(EventRepository):
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

    def __init__(self) -> None:
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
    def list(
        self,
        *,
        filter: EventFilterCriteria | None,
    ) -> list[Event]:
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
        events_list = list(self._storage.values())

        if filter is not None:
            events_list = _apply_filter_and_sort(events_list, filter=filter)

        logger.info(
            "Listing events in memory",
            total=len(events_list),
            filter=filter,
        )

        return events_list

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
            logger.warning(
                "Evento não encontrado em memória para update", event_id=event.id
            )
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

    # ----------------------------------------------------------------------
    # EXTRA (abstracts from EventRepository)
    # ----------------------------------------------------------------------
    def replace_all(self, events: list[Event]) -> list[Event]:
        """
        Completely replace all stored events with the given list.

        IDs from the incoming events are ignored: new IDs are generated
        to keep the behavior aligned with a 'fresh' database.

        This is primarily intended for tests or batch operations.
        """
        self._storage.clear()
        self._next_id = 1

        persisted: list[Event] = []
        for ev in events:
            ev.id = None  # força o repo a atribuir um novo ID
            persisted.append(self.add(ev))

        logger.info(
            "Todos os eventos foram substituídos em memória",
            total=len(persisted),
        )
        return persisted

    def replace_by_id(self, event_id: int, new_event: Event) -> Event:
        """
        Completely replace a single event by ID.

        Preserves the original `created_at` if the old event exists.
        """
        if event_id not in self._storage:
            logger.warning(
                "Tentativa de substituir evento inexistente em memória",
                event_id=event_id,
            )
            raise KeyError("Event not found")

        old = self._storage[event_id]
        new_event.id = event_id
        new_event.created_at = old.created_at
        new_event.updated_at = datetime.utcnow()

        self._storage[event_id] = new_event

        logger.info(
            "Evento substituído em memória",
            event_id=event_id,
            title=new_event.title,
        )
        return new_event

    def delete_all(self) -> None:
        """
        Remove todos os eventos e zera o contador de IDs.
        Útil em cenários de teste.
        """
        self._storage.clear()
        self._next_id = 1
        logger.info("Todos os eventos foram deletados em memória")
