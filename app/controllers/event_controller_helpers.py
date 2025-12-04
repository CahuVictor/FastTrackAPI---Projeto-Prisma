# app/controllers/event_controller_helpers.py
from __future__ import annotations

from typing import TypeVar, Type
from structlog import get_logger

from app.models.event import Event
from app.models.event_patch import EventPatch
from app.models.event_filters import EventFilterCriteria
from app.models.enums import EventStatus, EventEnvironment, AgeRestriction
from app.schemas.event.event_view import EventView
from app.schemas.event.event_filters import EventFilters
from app.schemas.event.event_csv_row import EventCsvRow
from app.schemas.event.event_create import EventCreate
from app.schemas.event.event_update import EventUpdate

logger = get_logger().bind(module="event_controller_helpers")


TEnum = TypeVar("TEnum")


def _parse_csv_str(raw: str | None) -> list[str] | None:
    if raw is None:
        return None
    items = [item.strip() for item in raw.split(",") if item.strip()]
    return items or None


def _parse_csv_enum(raw: str | None, enum_cls: Type[TEnum]) -> list[TEnum] | None:
    """
    Convert a comma-separated string into a list of Enum values.

    Raises ValueError if any value is invalid (pode ser tratado acima
    no controller se quiser transformar em HTTPException 400).
    """
    if raw is None:
        return None

    values: list[TEnum] = []
    for item in raw.split(","):
        token = item.strip()
        if not token:
            continue
        # permite case-insensitive se quiser:
        # ex: enum_cls(token.lower()) se os values forem lower
        values.append(enum_cls(token))
    return values or None


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
# EventCreate to Event
# ------------------------------------------------------------------ #
def from_event_create(schema: EventCreate) -> Event:
    """
    Map an `EventCreate` HTTP schema into a domain `Event` entity.

    This helper is responsible for translating the validated Pydantic
    payload received by the controller into a pure domain object,
    decoupling the service layer from HTTP concerns.

    Notes:
        - The `id`, `views`, and audit fields (`created_at`, `updated_at`,
          `deleted_at`, `created_by`, `updated_by`, `deleted_by`) are
          intentionally left for the repository/infrastructure layer to
          populate.
        - Default values (such as `age_restriction` or `environment`) are
          taken from the `EventCreate` schema, which already enforces
          validation and normalization rules.

    Args:
        schema:
            `EventCreate` instance validated by FastAPI/Pydantic.

    Returns:
        A new `Event` domain entity ready to be persisted by the
        service/repository layers.
    """
    return Event.create(
        # Core content
        title=schema.title,
        description=schema.description,
        status=schema.status,
        # Scheduling
        start_time=schema.start_time,
        end_time=schema.end_time,
        timezone=schema.timezone,
        # Context / classification
        city=schema.city,
        age_restriction=schema.age_restriction,
        expected_audience=schema.expected_audience,
        environment=schema.environment,
        # Engagement
        participants=schema.participants,
        created_by=None,  # se quiser, depois podemos receber o usuário aqui
    )


# ------------------------------------------------------------------ #
# EventCreate to Event
# ------------------------------------------------------------------ #
def from_event_update(schema: EventUpdate) -> EventPatch:
    """
    Map an `EventUpdate` HTTP schema into a domain-level `EventPatch`.

    This model is used by the service layer to apply partial changes to
    an existing `Event` without depending on HTTP-specific types.

    The mapping is straightforward: all optional fields from the update
    schema are copied into the patch. Fields left as `None` mean
    “no change” for that attribute.

    Args:
        schema:
            `EventUpdate` instance containing optional fields to patch.

    Returns:
        An `EventPatch` instance representing the requested changes.
    """
    # Usamos model_dump(exclude_unset=True) para ignorar campos
    # que o cliente não enviou (mantendo o conceito de "no change").
    data = schema.model_dump(exclude_unset=True)
    return EventPatch(**data)


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
    return EventFilterCriteria(
        # Pagination
        skip=schema.skip,
        limit=schema.limit,

        # Core content
        title=schema.title,
        description=schema.description,
        status=_parse_csv_enum(schema.status, EventStatus),

        # Scheduling
        start_from=schema.start_from,
        start_to=schema.start_to,

        # Context / classification
        city=schema.city,
        age_restriction=_parse_csv_enum(schema.age_restriction, AgeRestriction),
        expected_audience=schema.expected_audience,
        environment=_parse_csv_enum(schema.environment, EventEnvironment),

        # Engagement
        participants=_parse_csv_str(schema.participants),
        views_min=schema.views_min,
        views_max=schema.views_max,

        # Audit fields
        created_from=schema.created_from,
        created_to=schema.created_to,
        updated_from=schema.updated_from,
        updated_to=schema.updated_to,
        deleted_from=schema.deleted_from,
        deleted_to=schema.deleted_to,
        created_by=_parse_csv_str(schema.created_by),
        updated_by=_parse_csv_str(schema.updated_by),
        deleted_by=_parse_csv_str(schema.deleted_by),
    )


def to_event_filters(model: EventFilterCriteria) -> EventFilters:
    """
    Convert the domain-level `EventFilterCriteria` model back into the
    HTTP-level `EventFilters` schema (useful for tests or tooling).
    """
    return EventFilters.model_validate(model.__dict__)


# ------------------------------------------------------------------ #
# CSV row ? EventCreate mapper
# ------------------------------------------------------------------ #
def from_event_csv_row(row: EventCsvRow) -> Event:
    """
    Map an `EventCsvRow` (CSV representation) into a domain `Event`
    entity used by the service layer.

    This is where we apply domain-level conversions:
    - strings -> enums (EventStatus, EventEnvironment)
    - splitting participants string into a list
    - applying default values for optional fields

    Args:
        row:
            `EventCsvRow` instance built/validado a partir de uma linha do CSV.

    Returns:
        A new `Event` domain entity (with `id=None`, `views=0` and
        audit fields left for the repository layer to populate).
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

    return Event.create(
        title=row.title,
        description=row.description,
        status=status_enum,
        start_time=row.start_time,
        end_time=row.end_time,
        timezone=row.timezone,
        city=row.city,
        age_restriction=row.age_restriction or "Livre",
        expected_audience=getattr(row, "expected_audience", None),
        environment=environment_enum,
        participants=participants,
        created_by=None,
    )
