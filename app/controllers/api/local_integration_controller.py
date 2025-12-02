# app/controllers/api/local_integration_controller.py
from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from structlog import get_logger

from app.core.deps import provide_local_service
from app.schemas.local.local_external_search import ExternalLocalSearch
from app.schemas.local.local_external_import import ExternalLocalImport
from app.schemas.local.local_view import LocalView
from app.models.local_external_query import ExternalLocalQueryCriteria
from app.controllers.api.local_integration_controller_helpers import (
    from_external_local_search,
    from_external_local_import,
)
from app.controllers.local_controller_helpers import to_local_view  # reuso do mapper
from app.services.local_service import LocalService
from app.utils.http import raise_http

logger = get_logger().bind(module="local_external")

_provide_local_service = Depends(provide_local_service)

router = APIRouter(
    prefix="/local/external",
    tags=["local-external (Not Implemented)"],
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
    filters: ExternalLocalSearch = Depends(),
    service: LocalService = _provide_local_service,
) -> List[LocalView]:
    """
    Proxy search against the internal LocalInfo API.

    This endpoint does NOT persist venues in our database.
    It returns a list of Local-like views based on the external payload,
    allowing the caller (e.g., UI) to:
    - preview suggested venues;
    - decide whether to import a given venue into our own Local repository.
    
    The query parameters are first bound into an `ExternalLocalSearch` schema
    (HTTP layer) and then converted into an `ExternalLocalQueryCriteria`
    model (domain layer) before being passed to the service.
    """
    criteria = from_external_local_search(filters)
    
    logger.info("External Local search requested", criteria)

    try:
        # Talk to LocalService, which calls the external API and maps into domain
        locals_ = await service.search_locals_external(criteria=criteria)
    except NotImplementedError as exc:
        # # Silent for the client (no stacktrace), but logged as a warning
        # logger.warning("External LocalInfo API integration not implemented yet")
        raise_http(
            logger.warning,
            501,
            str(exc),
            criteria,
        )

    if not locals_:
        # você decide: 404 ou 200 com lista vazia.
        # se quiser manter 404, descomente a linha abaixo:
        # raise_http(logger.warning, 404, "No venues found in external API")
        return []

    # Note: these LocalView instances represent data from the external system,
    # not necessarily persisted in our own DB.
    return [to_local_view(local) for local in locals_]

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
    filters: ExternalLocalImport = Depends(),
    service: LocalService = _provide_local_service,
) -> list[LocalView]:
    """
    Import Locals from the external LocalInfo API, persisting them into
    the internal repository.

    The HTTP-level filters are first captured in an `ExternalLocalImport`
    schema and then converted into an `ExternalLocalQueryCriteria` that is
    consumed by the service layer.

    For now this endpoint is a placeholder that raises 501 until the
    integration is implemented.
    """
    criteria = from_external_local_import(filters)
    
    logger.info("Import Locals from the external", criteria)
    
    
    try:
        locals_ = await service.import_locals_from_external(criteria=criteria)
        
    except NotImplementedError as exc:
        raise_http(
            logger.info,
            501,
            str(exc),
            criteria,
        )

    return [LocalView.model_validate(local) for local in locals_]