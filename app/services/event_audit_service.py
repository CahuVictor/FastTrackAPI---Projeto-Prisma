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
from app.models.event_audit_filters import EventAuditFilterCriteria
from app.repositories.event_audit_repo import EventAuditRepository

logger = get_logger().bind(module="event_audit_service")


class EventAuditService:
    """
    Application service responsible for handling audit-related use cases
    for Events.

    It encapsulates how audit records are created and retrieved, and
    provides dedicated helper methods for common actions (created,
    updated, deleted, restored), plus query helpers used by the HTTP
    layer (controllers).
    """

    def __init__(self, repo: EventAuditRepository) -> None:
        """
        Initialize the service with a concrete EventAuditRepository.

        Args:
            repo:
                Concrete implementation of the audit repository, such as a
                SQLAlchemy-based repository or an in-memory version for tests.
        """
        self.repo = repo

    # ------------------------------------------------------------------ #
    # Core logging method                                                #
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
        Persist a generic audit log entry for the given Event.

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
                Timestamp of the change; defaults to now (UTC) if not provided.

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
    # Helper methods for common actions                                  #
    # ------------------------------------------------------------------ #
    def log_created(
        self,
        event: Event,
        *,
        changed_by: str | None,
        snapshot: dict[str, Any] | None = None,
    ) -> EventAuditTable:
        """
        Shortcut to register a 'created' audit entry for the given Event.
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
    # Query helpers (used by controllers)                                #
    # ------------------------------------------------------------------ #
    def list_by_event(self, event_id: int) -> List[EventAuditTable]:
        """
        Return the full audit trail for a given Event, without pagination.

        Args:
            event_id:
                ID of the Event whose audit logs should be returned.

        Returns:
            A list of `EventAuditTable` ordered according to repository
            implementation (typically by `changed_at` ascending or descending).
        """
        logs = self.repo.list_by_event(event_id)
        logger.info("Event audit logs fetched", event_id=event_id, total=len(logs))
        return logs

    def list_for_event(
        self,
        event_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[EventAuditTable]:
        """
        Return the audit trail for a given Event, with simple pagination.

        Args:
            event_id:
                ID of the Event whose audit logs should be returned.
            skip:
                How many records to skip (offset).
            limit:
                Maximum number of records to return.

        Returns:
            A list of `EventAuditTable` entries ordered by `changed_at`
            according to the repository implementation.
        """
        logs = self.repo.list_by_event(event_id)

        sliced = logs[skip : skip + limit]

        logger.info(
            "Audit logs fetched for single event",
            event_id=event_id,
            returned=len(sliced),
            skip=skip,
            limit=limit,
        )
        return sliced

    def list_all(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        action: Optional[EventAuditAction] = None,
        changed_by: Optional[str] = None,
    ) -> List[EventAuditTable]:
        """
        List all logs, optionally filtering by action or user.

        This method is mainly used by legacy or simpler endpoints that
        don't require the full filter DTO.

        Args:
            skip:
                How many records to skip (offset).
            limit:
                Maximum number of records to return.
            action:
                Optional filter by action enum.
            changed_by:
                Optional substring filter by `changed_by`.

        Returns:
            A paginated list of audit entries.
        """
        logs = self.repo.list_all()

        def _match(log: EventAuditTable) -> bool:
            if action and log.action != action:
                return False
            if changed_by and changed_by.lower() not in (log.changed_by or "").lower():
                return False
            return True

        filtered = [log for log in logs if _match(log)]
        sliced = filtered[skip : skip + limit]

        logger.info(
            "Audit logs fetched (all)",
            total=len(filtered),
            returned=len(sliced),
            skip=skip,
            limit=limit,
            action=action.value if action else None,
            changed_by=changed_by,
        )

        return sliced

    def list_recent(self, limit: int = 50) -> List[EventAuditTable]:
        """
        Return the most recent audit entries across all Events.

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
        filters: EventAuditFilterCriteria,
    ) -> List[EventAuditTable]:
        """
        List audit logs with optional filters and pagination.

        All filters are optional and combined using AND semantics.

        Args:
            filters:
                Domain-level filter criteria including pagination
                (skip, limit) and optional fields:
                - event_id
                - action (EventAuditAction)
                - changed_by (substring match, case-insensitive)
                - date_from (inclusive, UTC)
                - date_to   (inclusive, UTC)

        Returns:
            A list of audit entries that match the filters, sliced
            according to `filters.skip` and `filters.limit`.

        Notes:
            For now, this implementation loads all records from the
            repository and applies filtering in Python. When a SQL-backed
            repository is in use, this logic can be pushed down to SQL
            (WHERE / ORDER BY / LIMIT).
        """
        # For now, we keep a simple in-memory style implementation
        # built on top of `repo.list_all()`. If you later move to a
        # SQL-backed repo, this filtering can be pushed down to SQL.
        logs = self.repo.list_recent(limit=limit)

        def _matches(log: EventAuditTable) -> bool:
            # Event filter
            if filters.event_id is not None and log.event_id != filters.event_id:
                return False

            # Action filter
            if filters.action is not None and log.action != filters.action:
            	# supports both enum value and raw string comparisons
                return False

            # changed_by substring (case-insensitive)
            if filters.changed_by is not None:
                needle = filters.changed_by.lower()
                haystack = (log.changed_by or "").lower()
                if needle not in haystack:
                    return False

            # Date range filters
            if filters.date_from is not None and log.changed_at < filters.date_from:
                return False
            if filters.date_to is not None and log.changed_at > filters.date_to:
                return False

            return True

        filtered = [log for log in logs if _matches(log)]

        # Paginação: mesmo espírito dos outros filtros (0 = sem limite).
        skip = filters.skip or 0
        limit = filters.limit or 0

        if limit > 0:
            paginated = filtered[skip : skip + limit]
        else:
            paginated = filtered[skip:]

        logger.info(
            "Audit logs filtered",
            total=len(logs),
            matched=len(filtered),
            returned=len(paginated),
            filters=filters,
        )

        return paginated
