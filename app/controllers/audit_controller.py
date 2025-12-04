# app/controllers/audit_controller.py
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, Query
from structlog import get_logger

from app.core.rate_limit_config import limiter
from app.core.deps import provide_audit_service
from app.schemas.audit.audit_view import AuditView
from app.schemas.audit.audit_filters import AuditFilters
from app.models.enums import AuditAction
from app.controllers.audit_controller_helpers import from_audit_filters, to_audit_filters, to_audit_view
from app.services.audit_service import AuditService

logger = get_logger().bind(module="audit_controller")

router = APIRouter(
    prefix="/event-audit",
    tags=["event-audit (needed fix)"],
)

# Atalho para reutilizar o Depends em vários endpoints
_provide_audit_service = Depends(provide_audit_service)


@router.get(
    "/logs",
    summary="List audit logs with pagination and filters",
    response_model=List[AuditView],
    responses={
        200: {"description": "List of audit logs matching the given filters."},
    },
)
# @limiter.limit("60/minute")
def list_audit_logs(
    filters: Annotated[AuditFilters, Depends()],
    audit_service: AuditService = _provide_audit_service,
) -> List[AuditView]:
    """
    Return a paginated list of audit log entries.

    All filters are optional and combined using AND semantics. That is,
    an audit entry must satisfy **all** provided filters to be included
    in the result.

    Query parameters are automatically mapped into `AuditFilters`,
    then converted into a domain-level `AuditFilterCriteria` object
    and passed to the service layer.
    """
    criteria = from_audit_filters(filters)

    logger.info("Audit log query started", filters=criteria)

    logs = audit_service.list_logs(filters=criteria)

    logger.info(
        "Audit log query finished",
        returned=len(logs),
    )

    # `from_attributes=True` on AuditView allows direct ORM/domain objects here
    return [to_audit_view(log) for log in logs]