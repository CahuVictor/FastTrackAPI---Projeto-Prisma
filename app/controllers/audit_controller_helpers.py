# app/controllers/audit_controller_helpers.py
from __future__ import annotations

from structlog import get_logger

from app.schemas.audit.audit_view import AuditView
from app.schemas.audit.audit_filters import AuditFilters
from app.models.audit_log_command import AuditLogCommand
from app.models.audit_filters import AuditFilterCriteria

logger = get_logger().bind(module="audit_controller_helpers")

def from_audit_filters(schema: AuditFilters) -> AuditFilterCriteria:
    """
    Convert the HTTP-level `AuditFilters` schema into the
    domain-level `AuditFilterCriteria` model.
    """
    data = schema.model_dump()
    return AuditFilterCriteria(**data)


def to_audit_filters(model: AuditFilterCriteria) -> AuditFilters:
    """
    Convert the domain-level `AuditFilterCriteria` model back into the
    HTTP-level `AuditFilters` schema (useful for tests or tooling).
    """
    return AuditFilters.model_validate(model.__dict__)

def to_audit_view(model: AuditLogCommand) -> AuditView:
    """
    Map a persisted audit entry (AuditLogTable) into an `AuditView` schema.

    This helper is used by the controller layer to ensure a single,
    centralized mapping between the persistence model and the HTTP
    response schema, avoiding duplication and keeping the mapping
    consistent across all endpoints.

    Args:
        model: `AuditLogCommand` instance.

    Returns:
        An `AuditView` instance populated with data from the given entry.
    """
    # `from_attributes=True` on AuditView allows direct ORM/domain objects here
    return AuditView.model_validate(model)