# app/services/event_audit_service.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, List

from structlog import get_logger

from app.infra.db.tables.event_audit_table import (
    EventAuditTable,
    EventAuditAction,
)
from app.models.event import Event
from app.repositories.event_audit_repo import EventAuditRepository

logger = get_logger().bind(module="event_audit_service")

class EventAuditService:
    """
    Application service responsible for handling audit-related use cases
    for events.

    It encapsulates how audit records are created and retrieved, and
    provides dedicated helper methods for common actions (created,
    updated, deleted, restored).
    """

    def __init__(self, repo: EventAuditRepository) -> None:
        """
        Args:
            repo:
                Concrete implementation of the audit repository, such as a
                SQLAlchemy-based repository or an in-memory version for tests.
        """
        self.repo = repo

    # ------------------------------------------------------------------ #
    # Core logging method
    # ------------------------------------------------------------------ #
    def log_action(
        self,
        *,
        event_id: int,
        action: EventAuditAction,
        changed_by: str | None,
        changes: dict[str, Any] | None = None,
        snapshot: dict[str, Any] | None = None,
        changed_at: datetime | None = None,
    ) -> EventAuditTable:
        """
        Persist a generic audit log entry for the given event.

        Args:
            event_id:
                ID of the event that has been modified.
            action:
                High-level action type (created, updated, deleted, restored).
            changed_by:
                User identifier (username, ID, etc.) that performed the action.
            changes:
                Optional diff-like structure describing what changed.
            snapshot:
                Optional snapshot of the current event state.
            changed_at:
                Timestamp of the change; defaults to now if not provided.

        Returns:
            The persisted `EventAuditTable` instance.
        """
        effective_changed_at = changed_at or datetime.utcnow()

        audit = EventAuditTable(
            event_id=event_id,
            action=action,
            changed_at=effective_changed_at,
            changed_by=changed_by,
            changes=changes,
            snapshot=snapshot,
        )

        saved = self.repo.add(audit)
        logger.info(
            "Event audit log recorded",
            event_id=event_id,
            action=action.value,
            changed_by=changed_by,
        )
        return saved

    # ------------------------------------------------------------------ #
    # Helper methods for common actions
    # ------------------------------------------------------------------ #
    def log_created(
        self,
        event: Event,
        *,
        changed_by: str | None,
        snapshot: dict[str, Any] | None = None,
    ) -> EventAuditTable:
        """
        Shortcut to register a 'created' audit entry for the given event.
        """
        return self.log_action(
            event_id=event.id,  # type: ignore[arg-type]
            action=EventAuditAction.CREATED,
            changed_by=changed_by,
            changes=None,
            snapshot=snapshot,
        )

    def log_updated(
        self,
        event: Event,
        *,
        changed_by: str | None,
        changes: dict[str, Any] | None,
        snapshot: dict[str, Any] | None = None,
    ) -> EventAuditTable:
        """
        Shortcut to register an 'updated' audit entry.

        Args:
            event:
                Event domain entity after the update.
            changed_by:
                User responsible for the change.
            changes:
                Dict describing which fields changed and how, e.g.:

                {
                    "status": {"old": "draft", "new": "published"},
                    "expected_audience": {"old": 100, "new": 300}
                }
        """
        return self.log_action(
            event_id=event.id,  # type: ignore[arg-type]
            action=EventAuditAction.UPDATED,
            changed_by=changed_by,
            changes=changes,
            snapshot=snapshot,
        )

    def log_deleted(
        self,
        event: Event,
        *,
        changed_by: str | None,
        snapshot: dict[str, Any] | None = None,
    ) -> EventAuditTable:
        """
        Shortcut to register a 'deleted' (soft-delete) audit entry.
        """
        return self.log_action(
            event_id=event.id,  # type: ignore[arg-type]
            action=EventAuditAction.DELETED,
            changed_by=changed_by,
            changes=None,
            snapshot=snapshot,
        )

    def log_restored(
        self,
        event: Event,
        *,
        changed_by: str | None,
        snapshot: dict[str, Any] | None = None,
    ) -> EventAuditTable:
        """
        Shortcut to register a 'restored' audit entry (undo soft-delete).
        """
        return self.log_action(
            event_id=event.id,  # type: ignore[arg-type]
            action=EventAuditAction.RESTORED,
            changed_by=changed_by,
            changes=None,
            snapshot=snapshot,
        )

    # ------------------------------------------------------------------ #
    # Query helpers
    # ------------------------------------------------------------------ #
    def list_by_event(self, event_id: int) -> List[EventAuditTable]:
        """
        Return the full audit trail for a given event.

        Args:
            event_id:
                ID of the event whose audit logs should be returned.

        Returns:
            A list of `EventAuditTable` ordered according to repository
            implementation (typically by `changed_at` ascending or descending).
        """
        logs = self.repo.list_by_event(event_id)
        logger.info("Event audit logs fetched", event_id=event_id, total=len(logs))
        return logs

    def list_recent(self, limit: int = 50) -> List[EventAuditTable]:
        """
        Return the most recent audit entries across all events.

        Args:
            limit:
                Maximum number of records to return.

        Returns:
            A list of `EventAuditTable` ordered by recency.
        """
        logs = self.repo.list_recent(limit=limit)
        logger.info("Recent event audit logs fetched", total=len(logs), limit=limit)
        return logs

    def list_logs(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        event_id: int | None = None,
        action: str | None = None,
        changed_by: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> List[EventAuditTable]:
        """
        List audit logs with optional filters and pagination.

        All filters are optional and combined using AND semantics.

        Args:
            skip:
                How many records to skip (offset).
            limit:
                Maximum number of records to return.
            event_id:
                If provided, return only logs for this event id.
            action:
                If provided, return only logs with this action name.
            changed_by:
                If provided, filter logs whose `changed_by` contains this
                value (case-insensitive substring match).
            date_from:
                If provided, include only logs with `changed_at` greater
                than or equal to this value.
            date_to:
                If provided, include only logs with `changed_at` less
                than or equal to this value.

        Returns:
            A list of audit entries that match the filters, sliced
            according to `skip` and `limit`.
        """
        # For now, we keep a simple in-memory style implementation
        # built on top of `repo.list_all()`. If you later move to a
        # SQL-backed repo, this filtering can be pushed down to SQL.
        all_logs = self.repo.list_recent(limit=limit) # list_all()

        def _matches(log: EventAuditTable) -> bool:
            if event_id is not None and log.event_id != event_id:
                return False
            if action is not None and str(log.action) != action and log.action != action:
                # supports both enum value and raw string comparisons
                return False
            if changed_by is not None and changed_by.lower() not in (log.changed_by or "").lower():
                return False
            if date_from is not None and log.changed_at < date_from:
                return False
            if date_to is not None and log.changed_at > date_to:
                return False
            return True

        filtered = [log for log in all_logs if _matches(log)]
        paginated = filtered[skip : skip + limit]

        logger.info(
            "Audit logs filtered",
            total=len(all_logs),
            matched=len(filtered),
            returned=len(paginated),
            skip=skip,
            limit=limit,
            event_id=event_id,
            action=action,
            changed_by=changed_by,
        )
        return paginated