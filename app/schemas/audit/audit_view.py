# app/schemas/audit/audit_view.py
from __future__ import annotations

from datetime import datetime
from typing import Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import AuditAction, AuditEntityName


class AuditView(BaseModel):
    """
    Read model (view) for audit entries, generic for any table/entity.

    This schema is used by the HTTP layer to expose audit information
    without leaking ORM or internal DB details.
    """

    id: int = Field(
        ...,
        description="Audit entry identifier (primary key of the audit table).",
    )

    entity_name: str = Field(
        ...,
        description=(
            "Logical name of the audited entity/table "
            "(e.g. 'events', 'users', 'locals')."
        ),
    )

    row_id: int = Field(
        ...,
        description=(
            "Identifier of the affected row in the origin table. "
            "Combined with `entity_name` this uniquely identifies "
            "what was changed."
        ),
    )

    action: AuditAction = Field(
        ...,
        description=(
            "Type of change performed on the row "
            "(created, updated, deleted, soft_deleted, restored)."
        ),
    )

    changed_by_user_id: int | None = Field(
        None,
        description=(
            "ID of the user who performed the change, pointing to the "
            "Users table. May be null for system/anonymous operations."
        ),
        json_schema_extra={"example": 42},
    )

    changed_at: datetime = Field(
        ...,
        description="Timestamp (UTC) when the change was recorded.",
    )
    
    reason: str | None = Field(
        None,
        description=(
            "Optional human-readable explanation for the change "
            "(e.g. 'bulk import', 'admin manual correction')."
        ),
    )

    ip_address: str | None = Field(
        None,
        description="Optional IP address from where the change was triggered.",
        json_schema_extra={"example": "192.168.0.10"},
    )
    
    changes: dict[str, Any] | None = Field(
        None,
        description=(
            "??" # TODO
        ),
    )

    snapshot: dict[str, Any] | None = Field(
        None,
        description=(
            "Optional JSON snapshot of the row after the change. "
            "Useful for historical inspection, debugging and diffing."
        ),
    )

    model_config = ConfigDict(from_attributes=True)
