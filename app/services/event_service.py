# app/services/event_service.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import List
from structlog import get_logger

from app.models.event import Event
from app.models.event_local_enums import EventStatus
from app.repositories.event_repo import EventRepository
from app.schemas.event_create import EventCreate
from app.schemas.event_update import EventUpdate
from app.utils.h_events import order_and_slice, ensure_aware

from app.services.event_audit_service import EventAuditService, EventAuditAction

logger = get_logger().bind(module="event_service")

class EventService:
    """
    Application service responsible for use cases related to Events.

    It orchestrates:
    - mapping between HTTP schemas and the Event domain entity;
    - business rules (status, views, time-based filters);
    - calls to the EventRepository (SQLAlchemy, in-memory, etc.).
    - optional audit logging (EventAuditService).
    """

    def __init__(
        self,
        repo: EventRepository,
        audit_service: EventAuditService | None = None,
    ) -> None:
        """
        Args:
            repo:
                Concrete implementation of EventRepository used to
                persist and retrieve Event entities.
                (SQLAlchemy, InMemory, etc.).
            audit_service:
                Optional EventAuditService used to record audit logs.
                If None, audit logging is simply skipped.
        """
        self.repo = repo
        self.audit_service = audit_service
    
    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _safe_log_created(self, event: Event, changed_by: str | None) -> None:
        """
        Internal helper to log a 'created' action if audit_service is set.
        """
        if not self.audit_service or event.id is None:
            return
        self.audit_service.log_created(
            event=event,
            changed_by=changed_by,
            snapshot=self._snapshot_from_event(event),
        )

    def _safe_log_updated(
        self,
        event: Event,
        changed_by: str | None,
        changes: dict | None,
    ) -> None:
        """
        Internal helper to log an 'updated' action if audit_service is set.
        """
        if not self.audit_service or event.id is None:
            return
        self.audit_service.log_updated(
            event=event,
            changed_by=changed_by,
            changes=changes,
            snapshot=self._snapshot_from_event(event),
        )

    def _safe_log_deleted(self, event: Event, changed_by: str | None) -> None:
        """
        Internal helper to log a 'deleted' action if audit_service is set.
        """
        if not self.audit_service or event.id is None:
            return
        self.audit_service.log_deleted(
            event=event,
            changed_by=changed_by,
            snapshot=self._snapshot_from_event(event),
        )

    def _snapshot_from_event(self, event: Event) -> dict:
        """
        Build a simple JSON-serializable snapshot from the Event entity.

        This is intentionally compact; you can adjust fields as needed.
        """
        return {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "status": getattr(event, "status", None),
            "start_time": getattr(event, "start_time", None),
            "end_time": getattr(event, "end_time", None),
            "timezone": getattr(event, "timezone", None),
            "city": event.city,
            "age_restriction": getattr(event, "age_restriction", None),
            "participants": list(event.participants),
            "views": event.views,
            "created_at": event.created_at,
            "updated_at": event.updated_at,
        }

    # ------------------------------------------------------------------ #
    # Basic CRUD
    # ------------------------------------------------------------------ #
    def list_events(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        city: str | None = None,
    ) -> List[Event]:
        """
        List events with pagination and optional city filter.

        Args:
            skip: How many records to skip (offset).
            limit: Maximum number of records to return.
            city: If provided, filter events by this city.

        Returns:
            A list of Event domain entities.
        """
        events = self.repo.list(skip=skip, limit=limit, city=city)
        logger.info(
            "Events listed successfully", # "Eventos listados com sucesso",
            total=len(events),
            skip=skip,
            limit=limit,
            city=city,
        )
        return events

    def list_all_events(self) -> List[Event]:
        """
        List all events, without pagination.

        Returns:
            The complete list of Event entities.
        """
        events = self.repo.list(skip=0, limit=0, city=None)
        logger.info("All events listed", total=len(events)) # "Todos os eventos listados"
        return events

    def get_event(self, event_id: int) -> Event | None:
        """
        Retrieve a single event without changing its view count.

        Args:
            event_id: Identifier of the event.

        Returns:
            The Event entity if found, otherwise None.
        """
        event = self.repo.get(event_id)
        if event:
            logger.info("Event retrieved", event_id=event_id, title=event.title) # "Evento recuperado"
        else:
            logger.info("Event not found in get_event", event_id=event_id) # "Evento não encontrado em get_event"
        return event

    def view_event(self, event_id: int) -> Event:
        """
        Retrieve an event and increment its view counter.

        Args:
            event_id: Identifier of the event.

        Returns:
            The Event entity after persistence, with the incremented views.

        Raises:
            KeyError: If the event does not exist.
        """
        event = self.repo.get(event_id)
        if not event:
            logger.warning("Attempt to view non-existent event", event_id=event_id) # "Tentativa de visualizar evento inexistente"
            raise KeyError("Event not found")

        event.views += 1
        logger.info("Incrementing views", event_id=event_id, views=event.views) # "Incrementando views"
        updated = self.repo.update(event)
        return updated

    def create_event(self, payload: EventCreate, *, changed_by: str | None = None) -> Event:
        """
        Create a new event from the given payload.

        Args:
            payload:
                Validated EventCreate data.
            changed_by:
                Optional user identifier who initiated the creation.

        Returns:
            The created and persisted Event entity.
        """
        event = Event(
            # Core content
            title=payload.title,
            description=payload.description,
            status=payload.status,
            # Scheduling
            start_time=payload.start_time,
            end_time=payload.end_time,
            timezone=payload.timezone,
            # Context / classification
            city=payload.city,
            age_restriction=payload.age_restriction,
            # Engagement
            participants=payload.participants,
            # created_at/updated_at ficam a cargo do repo
        )
        created = self.repo.add(event)
        logger.info("Event created successfully", event_id=created.id, title=created.title) # "Evento criado com sucesso"
        
        # audit
        self._safe_log_created(created, changed_by=changed_by)
        
        return created

    def update_event(
        self,
        event_id: int,
        payload: EventUpdate,
        *,
        changed_by: str | None = None,
    ) -> Event:
        """
        Apply a partial update (patch) to an existing event.

        Args:
            event_id: Identifier of the event to update.
            payload: Partial data with fields to modify.
            changed_by: Optional user identifier who initiated the update.

        Returns:
            The updated and persisted Event entity.

        Raises:
            KeyError: If the event does not exist.
        """
        event = self.repo.get(event_id)
        if not event:
            logger.warning("Attempt to update non-existent event", event_id=event_id) # "Tentativa de atualizar evento inexistente"
            raise KeyError("Event not found")

        # build a simple changes diff
        changes: dict[str, dict[str, object]] = {}

        def _track_change(field: str, old, new) -> None:
            if old != new:
                changes[field] = {"old": old, "new": new}

        if payload.title is not None:
            _track_change("title", event.title, payload.title)
            event.title = payload.title
        if payload.description is not None:
            _track_change("description", event.description, payload.description)
            event.description = payload.description
        if payload.event_date is not None:
            _track_change("event_date", event.event_date, payload.event_date)
            event.event_date = payload.event_date
        if payload.city is not None:
            _track_change("city", event.city, payload.city)
            event.city = payload.city
        if payload.participants is not None:
            _track_change("participants", event.participants, payload.participants)
            event.participants = payload.participants

        updated = self.repo.update(event)
        logger.info("Event updated successfully", event_id=updated.id) # "Evento atualizado com sucesso"
        
        # audit only if something really changed
        if changes:
            self._safe_log_updated(updated, changed_by=changed_by, changes=changes)
            
        return updated

    def delete_event(self, event_id: int, *, changed_by: str | None = None) -> None:
        """
        Remove an existing event.

        Args:
            event_id: Identifier of the event to remove.
            changed_by: Optional user identifier who initiated the deletion.

        Raises:
            KeyError: If the event does not exist.
        """
        event = self.repo.get(event_id)
        if not event:
            logger.warning("Attempt to delete non-existent event", event_id=event_id) # "Tentativa de deletar evento inexistente"
            raise KeyError("Event not found")
        
        # capture snapshot before deletion
        self._safe_log_deleted(event, changed_by=changed_by)

        self.repo.delete(event_id)
        logger.info("Event deleted successfully", event_id=event_id) # "Evento deletado com sucesso"
    
    # ------------------------------------------------------------------ #
    # Advanced use cases (top soon, top viewed, batch, etc.)
    # ------------------------------------------------------------------ #
    def get_top_soon_events(self, limit: int) -> List[Event]:
        """
        Return the `limit` future events with the closest start times
        from now.

        Args:
            limit: Maximum number of events to return.

        Returns:
            List of future events ordered by `start_time` ascending.
        """
        # ✅ aware - retorna um datetime aware (com fuso horário)
        #     naive - não usar datetime naive (sem fuso horário), pois irá dificultar a ordenação depois na consulta
        now = datetime.now(timezone.utc)
        events = self.list_all_events()

        future_events = [
            ev for ev in events
            if ensure_aware(ev.event_date) >= now
        ]

        most_soon = order_and_slice(
            future_events,
            key_fn=lambda ev: ev.event_date,
            limit=limit,
        )

        logger.info(
            "Top soon events calculated", # "Eventos mais próximos calculados"
            total=len(most_soon),
            limit=limit,
        )
        return most_soon

    def get_top_viewed_events(self, limit: int) -> List[Event]:
        """
        Return the `limit` most viewed events.

        Sorting criteria:
        - `views` descending (most viewed first);
        - `start_time` ascending in case of ties.

        Args:
            limit: Maximum number of events to return.

        Returns:
            List of events ordered by popularity.
        """
        events = self.list_all_events()

        most_viewed = order_and_slice(
            events,
            key_fn=lambda ev: (-ev.views, ev.event_date),
            limit=limit,
        )

        logger.info(
            "Top viewed events calculated", # "Eventos mais vistos calculados",
            total=len(most_viewed),
            limit=limit,
        )
        return most_viewed

    def create_events_batch(self, payloads: List[EventCreate]) -> List[Event]:
        """
        Create multiple events in a single batch operation.

        Args:
            payloads: List of EventCreate payloads.

        Returns:
            List of newly created Event entities.
        """
        created_events: List[Event] = []
        for payload in payloads:
            created = self.create_event(payload)
            created_events.append(created)

        logger.info(
            "Events created in batch", # "Eventos criados em lote",
            total=len(created_events),
        )
        return created_events

    def replace_all_events(
        self,
        new_events: List[Event],
        *,
        changed_by: str | None = None,
    ) -> List[Event]:
        """
        Completely replace the event collection with a new list.

        Naive implementation:
        - delete all existing events;
        - insert all new events.

        Args:
            new_events: List of Event entities representing the desired
                        final state.
            changed_by: Optional user identifier who initiated the 
                        replacement.

        Returns:
            List of events that were persisted.
        """
        # remove todos
        existing = self.list_all_events()
        for ev in existing:
            # audit delete per event
            self._safe_log_deleted(ev, changed_by=changed_by)
            self.repo.delete(ev.id)  # type: ignore[arg-type]


        # adiciona todos novamente
        persisted: List[Event] = []
        for ev in new_events:
            # ignoramos created_at/updated_at informados de fora:
            # o repo é responsável por setar esses campos.
            ev.id = None  # garante que serão recriados
            persisted.append(self.repo.add(ev))
            # audit created per event
            self._safe_log_created(created, changed_by=changed_by)

        logger.info(
            "All events replaced", # "Todos os eventos foram substituídos",
            total=len(persisted),
        )
        return persisted

    def replace_event_by_id(
        self,
        event_id: int,
        new_event: Event,
        *,
        changed_by: str | None = None,
    ) -> Event:
        """
        Completely replace the data of a single event.

        Args:
            event_id: ID of the event to replace.
            new_event: Event entity containing the new data (except id).
            changed_by: Optional user identifier who initiated the replacement.

        Returns:
            Event entity after replacement.

        Raises:
            KeyError: If the event does not exist.
        """
        existing = self.repo.get(event_id)
        if not existing:
            logger.warning("Attempt to replace non-existent event", event_id=event_id) # "Tentativa de substituir evento inexistente"
            raise KeyError("Event not found")

        # Build a diff between existing and new_event if you want
        changes: dict[str, dict[str, object]] = {
            # Example: fill as desired
            # "title": {"old": existing.title, "new": new_event.title},
        }
        
        # preserva o id, mas deixa created_at/updated_at a cargo do repo
        new_event.id = event_id
        replaced = self.repo.update(new_event)

        logger.info(
            "Event fully replaced", # "Evento substituído por completo",
            event_id=event_id,
            title=replaced.title,
        )
        
        # log as UPDATED (or a custom action if you prefer)
        self._safe_log_updated(replaced, changed_by=changed_by, changes=changes or None)
        
        return replaced
