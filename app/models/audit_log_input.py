# app/models/audit_log_input.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.models.enums import AuditEntityName

# ---------------------------------------------------------------------- #
# Command/DTO classes for logging                                        #
# ---------------------------------------------------------------------- #

@dataclass(slots=True)
class AuditLogInput:
    """
    Input DTO used by public methods like `log_created`, `log_updated`, etc.

    It represents the *intent* to record an audit log, without forcing the
    caller a specific action type. The action is injected by the service.
    """
    entity_name: AuditEntityName
    row_id: int
    changed_by_user_id: int | None
    changes: dict[str, Any] | None = None
    snapshot: dict[str, Any] | None = None
    reason: str | None = None
    ip_address: str | None = None
    changed_at: datetime | None = None