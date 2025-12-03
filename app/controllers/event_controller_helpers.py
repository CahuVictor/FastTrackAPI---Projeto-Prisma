# app/controllers/event_controller_helpers.py
from __future__ import annotations

from structlog import get_logger

from app.models.event import Event
from app.models.event_filters import EventFilterCriteria
from app.models.enums import EventStatus, EventEnvironment
from app.schemas.event.event_view import EventView
from app.schemas.event.event_filters import EventFilters
from app.schemas.event.event_csv_row import EventCsvRow
from app.schemas.event.event_create import EventCreate

logger = get_logger().bind(module="event_controller_helpers")


# ------------------------------------------------------------------ #
# Event ? EventView mappers
# ------------------------------------------------------------------ #
def to_event_view(event: Event) -> EventView:
    """
    Map a domain `Event` entity into an `EventView` schema.

    This helper is used by the controller layer to ensure a single,
    centralized mapping between the domain model and the HTTP response
    schema, avoiding duplication and keeping the mapping consistent
    across all endpoints.

    Args:
        event: Domain `Event` instance.

    Returns:
        An `EventView` instance populated with data from the given event.
    """
    return EventView(
        id=event.id,  # type: ignore[arg-type]
        title=event.title,
        description=event.description,
        status=event.status,
        start_time=event.start_time,
        end_time=event.end_time,
        timezone=event.timezone,
        city=event.city or "",
        age_restriction=event.age_restriction,
        expected_audience=event.expected_audience,
        environment=event.environment,
        participants=event.participants,
        views=event.views,
        created_at=event.created_at,  # type: ignore[arg-type]
        updated_at=event.updated_at,
    )


def from_event_view(view: EventView) -> Event:
    """
    Map an `EventView` schema into a domain `Event` entity.

    This helper is intended for specific use cases where the API needs to
    accept a full event representation (e.g., replace endpoints) and
    convert it back into the domain model.

    Important:
        - The `id` field is taken from the view, but the service /
          repository layer is still responsible for enforcing or
          overriding the actual ID when persisting.
        - Audit-related fields such as `created_at` and `updated_at`
          should normally be controlled by the repository / infrastructure
          layer and not blindly trusted from the client.

    Args:
        view: An `EventView` instance received from the API layer.

    Returns:
        A domain `Event` entity built from the given view.
    """
    return Event(
        id=view.id,  # type: ignore[arg-type]
        title=view.title,
        description=view.description,
        status=view.status,
        start_time=view.start_time,
        end_time=view.end_time,
        timezone=view.timezone,
        city=view.city,
        age_restriction=view.age_restriction,
        expected_audience=view.expected_audience,
        environment=view.environment,
        participants=view.participants,
        views=view.views,
        created_at=view.created_at,
        updated_at=view.updated_at,
        deleted_at=None,
        created_by=None,
        updated_by=None,
        deleted_by=None,
    )


# ------------------------------------------------------------------ #
# Filters mappers (HTTP ? domain)
# ------------------------------------------------------------------ #
def from_event_filters(schema: EventFilters) -> EventFilterCriteria:
    """
    Convert the HTTP-level `EventFilters` schema into the
    domain-level `EventFilterCriteria` model.

    This keeps the controller decoupled from the internal filtering
    representation used by the service and repository layers.
    """
    data = schema.model_dump()
    return EventFilterCriteria(**data)


def to_event_filters(model: EventFilterCriteria) -> EventFilters:
    """
    Convert the domain-level `EventFilterCriteria` model back into the
    HTTP-level `EventFilters` schema (useful for tests or tooling).
    """
    return EventFilters.model_validate(model.__dict__)


# ------------------------------------------------------------------ #
# CSV row ? EventCreate mapper
# ------------------------------------------------------------------ #
def from_event_csv_row(row: EventCsvRow) -> EventCreate:
    """
    Map an `EventCsvRow` (CSV representation) into an `EventCreate`
    schema used by the service layer.

    This is where we apply domain-level conversions:
    - strings -> enums (EventStatus, EventEnvironment)
    - splitting participants string into a list
    """
    # Status
    if row.status:
        status_enum = EventStatus(row.status)
    else:
        status_enum = EventStatus.DRAFT

    # Environment
    environment_enum: EventEnvironment = EventEnvironment.UNRESTRICTED
    if row.environment:
        environment_enum = EventEnvironment(row.environment)

    # Participants
    participants: list[str] = []
    if row.participants_raw:
        participants = [
            p.strip() for p in row.participants_raw.split(";") if p.strip()
        ]

    return EventCreate(
        title=row.title,
        description=row.description,
        status=status_enum,
        start_time=row.start_time,
        end_time=row.end_time,
        timezone=row.timezone,
        city=row.city,
        age_restriction=row.age_restriction or "Livre",
        expected_audience=row.expected_audience,
        environment=environment_enum,
        participants=participants,
    )
