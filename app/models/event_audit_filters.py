# app/models/event_audit_filters.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel

from app.models.event_local_enums import EventStatus
from app.infra.db.tables.event_audit_table import EventAuditAction


@dataclass(slots=True)
class EventAuditFilterCriteria:
    """
    Domain-level filter model for events.

    This model is used by the service layer and can be translated to/from
    HTTP-level schemas or repository-specific filter mechanisms.
    """

    skip: int = 0
    limit: int = 20
    event_id: int | None = None
    action: EventAuditAction | None = None
    changed_by: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None