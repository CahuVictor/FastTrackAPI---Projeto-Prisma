# app/controllers/event_audit_controller_helpers.py
from __future__ import annotations

from structlog import get_logger

from app.models.event_audit_filters import EventAuditFilterCriteria
from app.schemas.event.event_audit_view import EventAuditView
from app.schemas.event.event_audit_filters import EventAuditFilters

logger = get_logger().bind(module="local_controller_helpers")

def from_event_audit_filters(schema: EventAuditFilters) -> EventAuditFilterCriteria:
    """
    Convert the HTTP-level `EventAuditFilters` schema into the
    domain-level `EventAuditFilterCriteria` model.
    """
    data = schema.model_dump()
    return EventAuditFilterCriteria(**data)


def to_event_audit_filters(model: EventAuditFilterCriteria) -> EventAuditFilters:
    """
    Convert the domain-level `EventAuditFilterCriteria` model back into the
    HTTP-level `EventAuditFilters` schema (useful for tests or tooling).
    """
    return EventAuditFilters.model_validate(model.__dict__)

def to_event_audit_view(model: EventAuditFilterCriteria) -> EventAuditView:
    """
    Map a domain `EventAuditFilterCriteria` entity into an `EventAuditView` schema.

    This helper is used by the controller layer to ensure a single,
    centralized mapping between the domain model and the HTTP response
    schema, avoiding duplication and keeping the mapping consistent
    across all endpoints.

    Args:
        event: Domain `EventAuditFilterCriteria` instance.

    Returns:
        An `EventAuditView` instance populated with data from the given event.
    """
    # `from_attributes=True` on EventAuditView allows direct ORM/domain objects here
    return EventAuditView.model_validate(model)