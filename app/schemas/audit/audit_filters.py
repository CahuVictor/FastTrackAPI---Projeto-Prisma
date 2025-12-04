# app/schemas/event/audit_filters.py
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.common.pagination_filters import PaginationFilters
from app.models.enums import AuditAction, AuditEntityName


class AuditFilters(PaginationFilters):
    """
    DTO used to represent all filters supported by the Audit listing API
    (currently focused on event-related audits, but generic enough to be
    reused for other entities).

    It is populated from query parameters in the controller and passed
    down to the service layer as a single object, avoiding endpoints
    with a huge number of parameters.

    This DTO is used between controller and service so that:
    - The controller can validate incoming query params once.
    - The service deals with a single, cohesive parameter object.
    - We can detect mismatches between endpoint params and filter fields.
    """
    # --- Domain filters -------------------------------------------------
    entity_name: Annotated[str | None, Field(
        default=None,
        description=(
            "Filter logs by the audited entity/table name "
            "(e.g. 'events', 'users', 'locals')."
        ),
        examples=["events"],
    )] = None

    row_id: Annotated[int | None, Field(
        default=None,
        description=(
            "Filter logs by the primary key value of the audited row "
            "in the origin table."
        ),
    )] = None

    action: Annotated[str | None, Field(
        default=None,
        description=(
            "Filter by action type "
            "(created, updated, deleted, soft_deleted, restored)."
        ),
    )] = None

    changed_by_user_id: Annotated[int | None, Field(
        default=None,
        description=(
            "Filter by the user identifier (User.id) that performed the "
            "change."
        ),
    )] = None

    date_from: Annotated[datetime | None, Field(
        default=None,
        description="Filter logs from this date (inclusive, UTC).",
    )] = None

    date_to: Annotated[datetime | None, Field(
        default=None,
        description="Filter logs up to this date (inclusive, UTC).",
    )] = None

    model_config = ConfigDict(
        extra="forbid",  # rejeita filtros desconhecidos
    )
