# app/controllers/event_audit_controller.py
from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from structlog import get_logger

from app.core.rate_limit_config import limiter
from app.core.deps import provide_event_audit_service
from app.schemas.event.event_audit_view import EventAuditView
from app.services.event_audit_service import EventAuditService

logger = get_logger().bind(module="event_audit")

router = APIRouter(
    prefix="/event-audit",
    tags=["event_audit"],
)

_provide_audit_service = Depends(provide_event_audit_service)


@router.get(
    "/logs",
    summary="List event audit logs with pagination and filters",
    response_model=List[EventAuditView],
    responses={
        200: {"description": "List of audit logs matching the given filters."},
    },
)
# @limiter.limit("60/minute")
def list_event_audit_logs(
    # Pagination
    skip: int = Query(
        0,
        ge=0,
        description="How many records to skip for pagination (offset).",
    ),
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Maximum number of records to return.",
    ),
    # Filters
    event_id: int | None = Query(
        None,
        description="Filter logs by the related event id.",
    ),
    action: str | None = Query(
        None,
        description="Filter by action type (e.g. 'created', 'updated', 'deleted').",
    ),
    changed_by: str | None = Query(
        None,
        description="Filter by the user/actor who performed the change (substring match).",
    ),
    date_from: datetime | None = Query(
        None,
        description="Filter logs from this date (inclusive, UTC).",
    ),
    date_to: datetime | None = Query(
        None,
        description="Filter logs up to this date (inclusive, UTC).",
    ),
    audit_service: EventAuditService = _provide_audit_service,
) -> List[EventAuditView]:
    """
    Return a paginated list of event audit entries.

    All filters are optional and combined using AND semantics. That is,
    an audit entry must satisfy **all** provided filters to be included
    in the result.
    """
    logger.info(
        "Audit log query started",
        skip=skip,
        limit=limit,
        event_id=event_id,
        action=action,
        changed_by=changed_by,
        date_from=date_from,
        date_to=date_to,
    )

    logs = audit_service.list_logs(
        skip=skip,
        limit=limit,
        event_id=event_id,
        action=action,
        changed_by=changed_by,
        date_from=date_from,
        date_to=date_to,
    )

    logger.info(
        "Audit log query finished",
        returned=len(logs),
    )

    # `from_attributes=True` on EventAuditView allows direct ORM/domain objects here
    return [EventAuditView.model_validate(log) for log in logs]
