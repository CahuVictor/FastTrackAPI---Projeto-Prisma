# app/infra/repositories/inmemory/event_audit_repo_inmemory.py
from __future__ import annotations

from typing import Dict, List
from structlog import get_logger

from app.infra.db.tables.event_audit_table import EventAuditTable
from app.repositories.event_audit_repo import EventAuditRepository

logger = get_logger().bind(module="event_audit_repo_inmemory")


class EventAuditRepoInMemory(EventAuditRepository):
    """
    In-memory implementation of EventAuditRepository.

    This repository is useful for:
    - unit tests (no database required);
    - local development where audit persistence is not critical;
    - prototyping features before wiring SQLAlchemy.

    The storage is **process-local** and will be lost when the app restarts.
    """

    def __init__(self) -> None:
        # simple in-memory store: audit_id -> EventAuditTable-like object
        self._storage: Dict[int, EventAuditTable] = {}
        self._next_id: int = 1

        logger.debug("EventAuditRepoInMemory initialized")

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #
    def _generate_id(self) -> int:
        """
        Generate a new incremental identifier for audit records.

        Returns:
            Integer ID that is unique within this in-memory repository.
        """
        new_id = self._next_id
        self._next_id += 1
        return new_id

    # ------------------------------------------------------------------ #
    # CREATE                                                             #
    # ------------------------------------------------------------------ #
    def add(self, audit: EventAuditTable) -> EventAuditTable:
        """
        Store a new audit log entry in memory.

        Args:
            audit:
                EventAuditTable instance to be stored. The `id` will be
                assigned by this repository if it is None.

        Returns:
            The same instance with `id` filled.
        """
        if audit.id is None:
            audit.id = self._generate_id()

        self._storage[audit.id] = audit

        logger.info(
            "Event audit stored in memory",
            audit_id=audit.id,
            event_id=audit.event_id,
            action=audit.action.value,
            changed_by=audit.changed_by,
        )

        return audit

    # ------------------------------------------------------------------ #
    # READ                                                              #
    # ------------------------------------------------------------------ #
    def list_by_event(self, event_id: int) -> List[EventAuditTable]:
        """
        Return all audit log entries for a given event.

        Args:
            event_id:
                ID of the event whose audit trail should be fetched.

        Returns:
            List of EventAuditTable entries ordered by `changed_at`
            ascending.
        """
        logs = [
            a
            for a in self._storage.values()
            if a.event_id == event_id
        ]
        logs.sort(key=lambda a: a.changed_at)

        logger.info(
            "Event audit logs fetched from memory by event",
            event_id=event_id,
            total=len(logs),
        )
        return logs

    # def list_all(self) -> List[EventAuditTable]:
    #     """
    #     Return all audit log entries stored in memory.

    #     Returns:
    #         List of EventAuditTable entries ordered by `changed_at`
    #         ascending.
    #     """
    #     logs = list(self._storage.values())
    #     logs.sort(key=lambda a: a.changed_at)

    #     logger.info(
    #         "All event audit logs fetched from memory",
    #         total=len(logs),
    #     )
    #     return logs

    def list_recent(self, limit: int = 50) -> List[EventAuditTable]:
        """
        Return the most recent audit log entries across all events.

        Args:
            limit:
                Maximum number of records to return. If <= 0, a default
                of 50 is used.

        Returns:
            List of EventAuditTable entries ordered by `changed_at`
            descending (most recent first).
        """
        if limit <= 0:
            limit = 50

        logs = list(self._storage.values())
        logs.sort(key=lambda a: a.changed_at, reverse=True)

        selected = logs[:limit]

        logger.info(
            "Recent event audits fetched from memory",
            total=len(selected),
            limit=limit,
        )
        return selected

	# # Opcional: helper para testes
    # def clear(self) -> None:
    #     """
    #     Clear all stored audit records (mainly for testing purposes).
    #     """
    #     self._storage.clear()
    #     self._next_id = 1
    #     logger.info("All in-memory event audit logs have been cleared")
