# app/services/event_audit_repo.py
from __future__ import annotations

from typing import List

from app.infra.db.tables.event_audit_table import EventAuditTable


class EventAuditRepository:
    """
    Minimal protocol-like interface expected by EventAuditService.

    You can implement this with SQLAlchemy, InMemory, etc.
    """

    def add(self, audit: EventAuditTable) -> EventAuditTable:  # pragma: no cover - protocol
        raise NotImplementedError

    def list_by_event(self, event_id: int) -> List[EventAuditTable]:  # pragma: no cover
        raise NotImplementedError

    def list_recent(self, limit: int = 50) -> List[EventAuditTable]:  # pragma: no cover
        raise NotImplementedError