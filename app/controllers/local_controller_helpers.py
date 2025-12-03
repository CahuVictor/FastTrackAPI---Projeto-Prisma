# app/controllers/local_controller_helpers.py
from __future__ import annotations

from structlog import get_logger

from app.models.local import Local
from app.models.local_filters import LocalFilterCriteria
from app.models.enums import VenueType, LocalSource
from app.schemas.local.local_create import LocalCreate
from app.schemas.local.local_view import LocalView
from app.schemas.local.local_filters import LocalFilters
from app.schemas.local.local_csv_row import LocalCsvRow

logger = get_logger().bind(module="local_controller_helpers")


# ------------------------------------------------------------------ #
# Local ↔ LocalView mappers
# ------------------------------------------------------------------ #
def to_local_view(local: Local) -> LocalView:
    """
    Map a domain `Local` entity into a `LocalView` schema.

    This helper is used by the controller layer to ensure a single,
    centralized mapping between the domain model and the HTTP response
    schema, avoiding duplication and keeping the mapping consistent
    across all endpoints.

    <test>
        This helper delegates to Pydantic's `model_validate` with
        `from_attributes=True` configured in LocalView. This keeps the mapping
        centralized and reduces duplication whenever new fields are added to
        the Local domain model.
    <test>

    Args:
        local: Domain `Local` instance.

    Returns:
        A `LocalView` instance populated with data from the given local.
    """
    return LocalView(
        id=local.id,  # type: ignore[arg-type]
        name=local.name,
        capacity=local.capacity,
        is_accessible=local.is_accessible,
        parking_available=local.parking_available,

        # Address Block
        address_street=local.address_street,
        address_city=local.address_city,
        address_state=local.address_state,

        # geo & timezone
        latitude=local.latitude,
        longitude=local.longitude,
        timezone=local.timezone,

        # integration and origin metadata
        external_id=local.external_id,
        source=local.source,

        # physical characteristics
        is_indoor=local.is_indoor,
        has_cover=local.has_cover,
        capacity_seated=local.capacity_seated,
        capacity_standing=local.capacity_standing,

        contact_phone=local.contact_phone,
        images=local.images,

        venue_type=local.venue_type,

        manually_edited=local.manually_edited,

        created_at=local.created_at,
        updated_at=local.updated_at,
    )


def from_local_view(view: LocalView) -> Local:
    """
    Map a `LocalView` schema into a domain `Local` entity.

    This helper is intended for specific use cases where the API needs to
    accept a full local representation (e.g., "replace" endpoints) and
    convert it back into the domain model.

    Important:
        - The `id` field can be provided by the view, but the service /
          repository layer is still responsible for enforcing or overriding
          the actual ID when persisting.
        - Audit-related fields such as `created_at` and `updated_at`
          should normally be controlled by the repository / infrastructure
          layer and not blindly trusted from the client.

    Args:
        view: A `LocalView` instance received from the API layer.

    Returns:
        A domain `Local` entity built from the given view.
    """
    return Local(
        id=view.id,  # type: ignore[arg-type]
        name=view.name,
        capacity=view.capacity,
        is_accessible=view.is_accessible,
        parking_available=view.parking_available,

        # Address Block
        address_street=view.address_street,
        address_city=view.address_city,
        address_state=view.address_state,

        # geo & timezone
        latitude=view.latitude,
        longitude=view.longitude,
        timezone=view.timezone,

        # integration and origin metadata
        external_id=view.external_id,
        source=view.source,

        # physical characteristics
        is_indoor=view.is_indoor,
        has_cover=view.has_cover,
        capacity_seated=view.capacity_seated,
        capacity_standing=view.capacity_standing,

        contact_phone=view.contact_phone,
        images=view.images,

        venue_type=view.venue_type,

        manually_edited=view.manually_edited,

        created_at=view.created_at,
        updated_at=view.updated_at,
    )

def from_local_filters(schema: LocalFilters) -> LocalFilterCriteria:
    """
    Convert the HTTP-level `LocalFilters` schema into the
    domain-level `LocalFilterCriteria` model.
    """
    data = schema.model_dump()
    return LocalFilterCriteria(**data)


def to_local_filters(model: LocalFilterCriteria) -> LocalFilters:
    """
    Convert the domain-level `LocalFilterCriteria` model back into the
    HTTP-level `LocalFilters` schema (useful for tests or tooling).
    """
    return LocalFilters.model_validate(model.__dict__)


def _parse_boolish(value: str | None) -> bool:
    """
    Convert common truthy strings into Python bool.

    Accepted truthy examples: '1', 'true', 'yes', 'y', 'sim'.
    Everything else (including None / '') is treated as False.
    """
    if value is None:
        return False
    v = value.strip().lower()
    return v in {"1", "true", "yes", "y", "sim"}

def from_local_csv_row(row: LocalCsvRow) -> LocalCreate:
    """
    Map a LocalCsvRow (CSV representation) into a LocalCreate schema
    used by the service layer.

    This is where we apply domain-level conversions:
    - strings -> enums (VenueType, LocalSource)
    - string flags -> booleans
    """
    venue_type_enum: VenueType | None = None
    if row.venue_type:
        venue_type_enum = VenueType(row.venue_type)

    source_enum: LocalSource | None = None
    if row.source:
        source_enum = LocalSource(row.source)

    is_accessible = _parse_boolish(row.is_accessible_raw)
    is_indoor = _parse_boolish(row.is_indoor_raw)
    has_cover = _parse_boolish(row.has_cover_raw)

    return LocalCreate(
        name=row.name,
        capacity=row.capacity,
        venue_type=venue_type_enum,
        is_accessible=is_accessible,
        address=row.address,
        external_id=row.external_id,
        source=source_enum,
        is_indoor=is_indoor,
        has_cover=has_cover,
        capacity_seated=row.capacity_seated,
        capacity_standing=row.capacity_standing,
        latitude=row.latitude,
        longitude=row.longitude,
        timezone=row.timezone,
    )