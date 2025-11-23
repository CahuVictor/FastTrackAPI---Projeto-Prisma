# app/controllers/api/local_integration_controller.py
from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from structlog import get_logger

from app.core.deps import provide_local_service
from app.models.event_local_enums import VenueType
from app.schemas.local.local_view import LocalView
from app.services.local_service import LocalService
from app.utils.http import raise_http

logger = get_logger().bind(module="local_external")

_provide_local_service = Depends(provide_local_service)

router = APIRouter(
    prefix="/local/external",
    tags=["local-external"],
    # dependencies=[auth_dep]
)


@router.get(
    "/search",
    summary="Search venues in the internal LocalInfo API",
    response_model=List[LocalView],
    responses={
        200: {"description": "Matching venues returned from external API."},
        404: {"description": "No venues found for the given filters."},
        501: {"description": "External LocalInfo integration not implemented yet."},
    },
)
async def search_external_locals(
    location_name: str | None = Query(
        None,
        description="Name or partial name of the venue (fuzzy match may be applied by the external API).",
    ),
    capacity_min: int | None = Query(
        None,
        description="Minimum capacity (inclusive).",
    ),
    capacity_max: int | None = Query(
        None,
        description="Maximum capacity (inclusive).",
    ),
    venue_types: list[VenueType] | None = Query(
        None,
        description="List of allowed venue types.",
    ),
    is_accessible: bool | None = Query(
        None,
        description="Filter by accessibility flag.",
    ),
    address: str | None = Query(
        None,
        description="Address or partial address (fuzzy match may be applied).",
    ),
    skip: int = Query(0, ge=0, description="How many records to skip"),
    limit: int = Query(20, le=100, description="Page size"),
    service: LocalService = _provide_local_service,
) -> List[LocalView]:
    """
    Proxy search against the internal LocalInfo API.

    This endpoint does NOT persist venues in our database.
    It returns a list of Local-like views based on the external payload,
    allowing the caller (e.g., UI) to:
    - preview suggested venues;
    - decide whether to import a given venue into our own Local repository.
    """
    logger.info(
        "External LocalInfo search requested",
        location_name=location_name,
        capacity_min=capacity_min,
        capacity_max=capacity_max,
        venue_types=venue_types,
        is_accessible=is_accessible,
        address=address,
        skip=skip,
        limit=limit,
    )

    try:
        # Talk to LocalService, which calls the external API and maps into domain
        locals_ = await service.search_locals_external(
            location_name=location_name,
            capacity_min=capacity_min,
            capacity_max=capacity_max,
            venue_types=venue_types,
            is_accessible=is_accessible,
            address=address,
            skip=skip,
            limit=limit,
        )
    except NotImplementedError:
        # Silent for the client (no stacktrace), but logged as a warning
        logger.warning("External LocalInfo API integration not implemented yet")
        raise_http(
            logger.warning,
            501,
            "External LocalInfo API integration not implemented yet",
        )

    if not locals_:
        # você decide: 404 ou 200 com lista vazia.
        # se quiser manter 404, descomente a linha abaixo:
        # raise_http(logger.warning, 404, "No venues found in external API")
        return []

    # Note: these LocalView instances represent data from the external system,
    # not necessarily persisted in our own DB.
    return [
        LocalView(
            id=local.id,  # likely None, since they are not persisted
            location_name=local.location_name,
            capacity=local.capacity,
            venue_type=local.venue_type,
            is_accessible=local.is_accessible,
            address=local.address,
            manually_edited=local.manually_edited,
            created_at=local.created_at,
            updated_at=local.updated_at,
        )
        for local in locals_
    ]

@router.post(
    "/{local_id}/sync-from-external",
    summary="Synchronize a Local with the external LocalInfo API",
    response_model=LocalView,
    responses={
        200: {"description": "Local synchronized successfully (when implemented)."},
        404: {"description": "Local not found."},
        501: {"description": "Sync not implemented yet."},
    },
)
async def sync_local_from_external(
    local_id: int,
    service: LocalService = _provide_local_service,
) -> LocalView:
    """
    Trigger a synchronization of a Local with the external LocalInfo API.

    Currently this endpoint is a placeholder and will return 501 until the
    integration is implemented.
    """
    try:
        local = await service.sync_local_from_external(local_id)
    except KeyError:
        raise_http(logger.warning, 404, "Local not found", local_id=local_id)
    except NotImplementedError as exc:
        raise_http(
            logger.info,
            501,
            str(exc),
            local_id=local_id,
        )

    return LocalView.model_validate(local)


@router.post(
    "/import-from-external",
    summary="Import locals from the external LocalInfo API into the internal store",
    response_model=list[LocalView],
    responses={
        200: {"description": "Locals imported successfully (when implemented)."},
        501: {"description": "Import not implemented yet."},
    },
)
async def import_locals_from_external(
    location_name: str | None = Query(None, description="Filter by name (partial match allowed)"),
    capacity_min: int | None = Query(None, ge=0, description="Minimum capacity"),
    capacity_max: int | None = Query(None, ge=0, description="Maximum capacity"),
    venue_types: list[VenueType] | None = Query(
        None, description="One or more venue types to filter"
    ),
    is_accessible: bool | None = Query(None, description="Filter by accessibility flag"),
    address: str | None = Query(None, description="Filter by address"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of locals to import"),
    service: LocalService = _provide_local_service,
) -> list[LocalView]:
    """
    Import Locals from the external LocalInfo API, persisting them into
    the internal repository.

    For now this endpoint is a placeholder that returns a 501 (Not Implemented).
    """
    try:
        locals_ = await service.import_locals_from_external(
            location_name=location_name,
            capacity_min=capacity_min,
            capacity_max=capacity_max,
            venue_types=venue_types,
            is_accessible=is_accessible,
            address=address,
            limit=limit,
        )
    except NotImplementedError as exc:
        raise_http(
            logger.info,
            501,
            str(exc),
            location_name=location_name,
            capacity_min=capacity_min,
            capacity_max=capacity_max,
        )

    return [LocalView.model_validate(local) for local in locals_]