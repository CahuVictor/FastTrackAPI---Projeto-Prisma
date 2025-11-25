# app/infra/repositories/sqlalchemy/event_audit_repo_sqlalchemy.py
from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session
from structlog import get_logger

from app.infra.db.tables.event_audit_table import (
    EventAuditTable,
    EventAuditAction,
)
from app.repositories.event_audit_repo import EventAuditRepository

logger = get_logger().bind(module="event_audit_repo_sqlalchemy")


class EventAuditRepoSQLAlchemy(EventAuditRepository):
    """
    SQLAlchemy-based repository for EventAuditTable.

    This repository is responsible for:
    - Persisting audit log entries.
    - Querying audit logs by event.
    - Querying the most recent audit logs globally.
    """

    def __init__(self, session: Session) -> None:
        """
        Args:
            session:
                SQLAlchemy session used to interact with the database.
        """
        self.session = session

    # ------------------------------------------------------------------ #
    # CREATE
    # ------------------------------------------------------------------ #
    def add(self, audit: EventAuditTable) -> EventAuditTable:
        """
        Persist a new audit log entry.

        Args:
            audit:
                Instance of EventAuditTable to be persisted.

        Returns:
            The same instance after being flushed (with `id` filled).
        """
        self.session.add(audit)
        self.session.flush()

        logger.info(
            "Event audit persisted",
            audit_id=audit.id,
            event_id=audit.event_id,
            action=audit.action.value,
            changed_by=audit.changed_by,
        )
        return audit

    # ------------------------------------------------------------------ #
    # READ
    # ------------------------------------------------------------------ #
    def list_by_event(self, event_id: int) -> List[EventAuditTable]:
        """
        Return all audit log entries for a given event.

        Args:
            event_id:
                ID of the event whose audit trail should be fetched.

        Returns:
            A list of EventAuditTable entries ordered by `changed_at`
            (ascending by default).
        """
        query = (
            self.session.query(EventAuditTable)
            .filter(EventAuditTable.event_id == event_id)
            .order_by(EventAuditTable.changed_at.asc())
        )

        logs = list(query.all())

        logger.info(
            "Event audit logs fetched by event",
            event_id=event_id,
            total=len(logs),
        )
        return logs

    def list_recent(self, limit: int = 50) -> List[EventAuditTable]:
        """
        Return the most recent audit log entries across all events.

        Args:
            limit:
                Maximum number of records to return.

        Returns:
            A list of EventAuditTable entries ordered by `changed_at`
            descending (most recent first).
        """
        if limit <= 0:
            limit = 50  # sensible default

        query = (
            self.session.query(EventAuditTable)
            .order_by(EventAuditTable.changed_at.desc())
            .limit(limit)
        )

        logs = list(query.all())

        logger.info(
            "Recent event audit logs fetched",
            total=len(logs),
            limit=limit,
        )
        return logs
