# app/schemas/event/event_audit_filters.py
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.common.pagination_filters import PaginationFilters
from app.infra.db.tables.event_audit_table import EventAuditAction


class EventAuditFilters(PaginationFilters):
    """
    DTO used to represent all filters supported by the Event Audit listing API.

    It is populated from query parameters in the controller and passed
    down to the service layer as a single object, avoiding endpoints
    with a huge number of parameters.

    Strongly-typed filter object for listing EventAudit entries.

    This DTO is used between controller and service so that:
    - The controller can validate incoming query params once.
    - The service deals with a single, cohesive parameter object.
    - We can detect mismatches between endpoint params and filter fields.
    """
    # Filtros de domínio
    event_id: Annotated[int | None, Field(
        description="Filter logs by the related event id.",
    )] = None

    action: Annotated[EventAuditAction | None, Field(
        description="Filter by action type (created, updated, deleted, restored).",
    )] = None

    changed_by: Annotated[str | None, Field(
        description="Filter by the user/actor who performed the change (substring match).",
    )] = None

    date_from: Annotated[datetime | None, Field(
        description="Filter logs from this date (inclusive, UTC).",
    )] = None

    date_to: Annotated[datetime | None, Field(
        description="Filter logs up to this date (inclusive, UTC).",
    )] = None

    model_config = ConfigDict(
        extra="forbid",  # rejeita filtros desconhecidos
    )
