# app/controllers/event_audit_controller.py
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, Query
from structlog import get_logger

from app.core.rate_limit_config import limiter
from app.core.deps import provide_event_audit_service
from app.schemas.event.event_audit_view import EventAuditView
from app.schemas.event.event_audit_filters import EventAuditFilters
from app.controllers.event_audit_controller_helpers import from_event_audit_filters, to_event_audit_filters, to_event_audit_view
from app.services.event_audit_service import EventAuditService, EventAuditAction

logger = get_logger().bind(module="event_audit_controller")

router = APIRouter(
    prefix="/event-audit",
    tags=["event_audit (needed fix)"],
)

# Atalho para reutilizar o Depends em vários endpoints
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
    filters: Annotated[EventAuditFilters, Depends()],
    audit_service: EventAuditService = _provide_audit_service,
) -> List[EventAuditView]:
    """
    Return a paginated list of event audit entries.

    All filters are optional and combined using AND semantics. That is,
    an audit entry must satisfy **all** provided filters to be included
    in the result.

    Query parameters are automatically mapped into `EventAuditFilters`,
    which is then passed to the service layer.
    """
    filter_model = from_event_audit_filters(filters)
    
    logger.info("Audit log query started", filters=filter_model)

    logs = audit_service.list_logs(filters=filter_model)

    logger.info(
        "Audit log query finished",
        returned=len(logs),
    )

    # `from_attributes=True` on EventAuditView allows direct
    # ORM/domain objects here
    return [to_event_audit_view(log) for log in logs]