# app/schemas/event_audit_view.py
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class EventAuditView(BaseModel):
    """
    Read model (view) for event audit entries.

    This schema is used by the HTTP layer to expose audit information
    without leaking ORM details.
    """

    id: int = Field(..., description="Audit entry identifier.")
    event_id: int = Field(..., description="Identifier of the related event.")
    action: str = Field(
        ...,
        description=(
            "Type of change performed on the event "
            "(e.g. 'created', 'updated', 'deleted', 'soft_deleted', 'restored')."
        ),
    )
    changed_by: str = Field(
        ...,
        description="User or actor who performed the change.",
        json_schema_extra={"example": "admin@example.com"},
    )
    changed_at: datetime = Field(
        ...,
        description="Timestamp (UTC) when the change happened.",
    )
    reason: str | None = Field(
        None,
        description="Optional human-readable explanation for the change.",
    )
    ip_address: str | None = Field(
        None,
        description="Optional IP address from where the change was triggered.",
        json_schema_extra={"example": "192.168.0.10"},
    )
    snapshot: dict[str, Any] | None = Field(
        None,
        description=(
            "Optional JSON snapshot of the event after the change. "
            "Useful for historical inspection and debugging."
        ),
    )

    model_config = ConfigDict(from_attributes=True)
