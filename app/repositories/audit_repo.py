# app/services/audit_repo.py
from __future__ import annotations

from typing import List

from app.models.audit_log_command import AuditLogCommand
from app.models.audit_filters import AuditFilterCriteria


class AuditRepository:
    """
    Minimal protocol-like interface expected by AuditService.

    You can implement this with SQLAlchemy, InMemory, etc.
    """

    def add(self, audit: AuditLogCommand) -> AuditLogCommand:  # pragma: no cover - protocol
        raise NotImplementedError

    def list_by_event(self, event_id: int) -> List[AuditLogCommand]:  # pragma: no cover
        raise NotImplementedError
    
    def list(self, *, filter: AuditFilterCriteria | None = None) -> list[AuditLogCommand]:  # pragma: no cover
        raise NotImplementedError

    def list_recent(self, limit: int = 50) -> List[AuditLogCommand]:  # pragma: no cover
        raise NotImplementedError