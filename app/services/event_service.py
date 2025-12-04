# app/services/event_service.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Any, Dict
from structlog import get_logger

from app.models.event import Event
from app.models.event_patch import EventPatch
from app.models.event_filters import EventFilterCriteria
from app.repositories.event_repo import EventRepository
from app.utils.h_events import order_and_slice, ensure_aware

from app.services.event_audit_service import EventAuditService, EventAuditAction

logger = get_logger().bind(module="event_service")

def _apply_event_changes(
    event: Event,
    payload: EventPatch,
) -> tuple[Event, Dict[str, Dict[str, Any]]]:
    """
    Apply partial changes from `payload` onto the given `event`.

    For each non-None field in `payload`, the corresponding attribute in
    `event` is updated. A `changes` dictionary is built describing the
    modifications performed.

    Args:
        event:
            The current persisted Event entity loaded from the repository.
        patch:
            The patch model containing optional new values.

    Returns:
        A tuple `(event, changes)` where:
            - `event` is the same instance, mutated with the new values;
            - `changes` is a dict in the form:
                {
                    "field_name": {"old": old_value, "new": new_value},
                    ...
                }
              representing only the fields that actually changed.
    """
    changes: Dict[str, Dict[str, Any]] = {}

    def _track_and_set(field: str, new_value: Any) -> None:
        old_value = getattr(event, field)
        if old_value != new_value:
            changes[field] = {"old": old_value, "new": new_value}
            setattr(event, field, new_value)

    # Lista dos campos do domínio que podem ser atualizados via patch
    candidate_fields = [
        "title",
        "description",
        "status",
        "start_time",
        "end_time",
        "timezone",
        "city",
        "age_restriction",
        "expected_audience",
        "environment",
        "participants",
    ]

    for field in candidate_fields:
        if hasattr(payload, field):
            value = getattr(payload, field)
            # Em patch, None significa "não enviar alteração"
            if value is not None:
                _track_and_set(field, value)

    return event, changes

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
        filters: EventFilterCriteria,
    ) -> List[Event]:
        """
        List events with pagination and optional city filter.

        Args:
            filters: Domain-level filter criteria including pagination,
                city, status and optional start_time range.

        Returns:
            List of `Event` domain entities that match the filters.
        """
        events = self.repo.list(filter=filters)
        
        logger.info(
            "Events listed successfully",
            total=len(events),
            filters=filters,
        )
        return events

    def list_all_events(self) -> List[Event]:
        """
        List all events, without pagination.

        Returns:
            The complete list of Event entities.
        """
        events = self.repo.list()
        
        logger.info("All events listed", total=len(events))
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

    def create_event(self, event: Event, *, changed_by: int | None = None) -> Event:
        """
        Create a new event from the given domain entity.

        Args:
            payload:
                Validated Event data.
            changed_by:
                Optional user identifier who initiated the creation.

        Returns:
            The created and persisted Event entity.
        """
        created = self.repo.add(event)
        
        logger.info("Event created successfully", event_id=created.id, title=created.title) # "Evento criado com sucesso"
        
        # audit
        self._safe_log_created(created, changed_by=None)  # TODO adicionar o changed_by_user_id
        
        return created

    def update_event(
        self,
        event_id: int,
        patch: EventPatch,
        *,
        changed_by: int | None = None,
    ) -> Event:
        """
        Apply a partial update (patch) to an existing event.

        Args:
            event_id: Identifier of the event to update.
            patch: Domain-level `EventPatch` with fields to modify.
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

        # Aplica alterações e coleta diff
        event, changes = _apply_event_changes(event, patch)
        
        # audit only if something really changed
        if changes:
            updated = self.repo.update(event)
            logger.info("Event updated successfully", event_id=updated.id) # "Evento atualizado com sucesso"
        
            # audit only if something really changed
            self._safe_log_updated(updated, changed_by=None, changes=changes) # TODO adicionar o changed_by_user_id
            
            return updated
        else:
            # Não houve mudança – nada a persistir
            logger.debug(
                "Event update had no effect (no fields changed)",
                event_id=event.id,
            )
            return event

    def delete_event(self, event_id: int, *, changed_by: int | None = None) -> None:
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
        self._safe_log_deleted(event, changed_by=None) # TODO adicionar o changed_by_user_id

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
            if ensure_aware(ev.start_time) >= now
        ]

        most_soon = order_and_slice(
            future_events,
            key_fn=lambda ev: ev.start_time,
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
            key_fn=lambda ev: (-ev.views, ev.start_time),
            limit=limit,
        )

        logger.info(
            "Top viewed events calculated", # "Eventos mais vistos calculados",
            total=len(most_viewed),
            limit=limit,
        )
        return most_viewed

    def create_events_batch(self, events: List[Event], *, changed_by: int | None = None,) -> List[Event]:
        """
        Create multiple events in a single batch operation.

        Args:
            events: List of domain `Event` entities (usually created from
                HTTP payloads at the controller layer).
            changed_by: Optional user identifier.

        Returns:
            List of newly created Event entities.
        """
        created_events: List[Event] = []
        for event in events:
            created = self.create_event(event)
            self._safe_log_created(created, changed_by=None) # TODO adicionar o changed_by_user_id
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
        changed_by: int | None = None,
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
            self._safe_log_deleted(ev, changed_by=None) # TODO adicionar o changed_by_user_id
            self.repo.delete(ev.id)  # type: ignore[arg-type]


        # adiciona todos novamente
        persisted: List[Event] = []
        for ev in new_events:
            # ignoramos created_at/updated_at informados de fora:
            # o repo é responsável por setar esses campos.
            ev.id = None  # garante que serão recriados
            created = self.repo.add(ev)
            persisted.append(created)
            # audit created per event
            self._safe_log_created(created, changed_by=None) # TODO adicionar o changed_by_user_id

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
        changed_by: int | None = None,
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
        self._safe_log_updated(replaced, changed_by=None, changes=changes or None) # TODO adicionar o changed_by_user_id
        
        return replaced
