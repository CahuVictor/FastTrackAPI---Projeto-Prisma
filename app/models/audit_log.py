# app/models/audit_log.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Literal

AuditOperation = Literal["INSERT", "UPDATE", "DELETE"]


@dataclass
class AuditLogEntry:
    """
    In-memory representation of an audit log entry.
    This is the logical equivalent of the "audit_log" table.
    """
    occurred_at: datetime
    user_id: Optional[str]
    table_name: str
    operation: AuditOperation
    row_pk: Dict[str, Any]
    changed: Dict[str, Dict[str, Any]]
    request_id: Optional[str] = None

    @classmethod
    def now(
        cls,
        *,
        table_name: str,
        operation: AuditOperation,
        row_pk: Dict[str, Any],
        changed: Dict[str, Dict[str, Any]],
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> "AuditLogEntry":
        return cls(
            occurred_at=datetime.now(timezone.utc),
            user_id=user_id,
            table_name=table_name,
            operation=operation,
            row_pk=row_pk,
            changed=changed,
            request_id=request_id,
        )
