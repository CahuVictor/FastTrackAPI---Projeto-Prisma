# app/controllers/local_controller.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Body, UploadFile, File, BackgroundTasks, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from structlog import get_logger
from io import StringIO
import csv
from typing import Iterable, Set, Type, Annotated

from app.controllers.local_controller_helpers import to_local_view, from_local_view, to_local_filters, from_local_filters, from_local_csv_row
# from app.core.rate_limit_config import limiter
from app.core.deps import provide_event_service, provide_local_service
from app.schemas.local.local_create import LocalCreate
from app.schemas.local.local_update import LocalUpdate
from app.schemas.local.local_view import LocalView
from app.schemas.local.local_filters import LocalFilters
from app.schemas.local.local_conflict_group import LocalConflictGroup
from app.schemas.local.local_merge_request import LocalMergeRequest
from app.schemas.local.local_csv_row import LocalCsvRow
from app.models.local import Local
from app.models.event_local_enums import VenueType
from app.services.event_service import EventService
from app.services.local_service import LocalService
from app.services.errors import DuplicateLocalError
from app.infra.cache.cache import cached_json
from app.utils.http import raise_http
from app.utils.security import require_roles, auth_dep # TODO Essas funções deveriam estar em úteis, elas usam classes da camada service

logger = get_logger().bind(module="local")

_provide_event_service = Depends(provide_event_service)
_provide_local_service = Depends(provide_local_service)

router = APIRouter(
    prefix="/local",
    tags=["local"],
    # dependencies=[auth_dep]
)


# ---------------------------------------------------------------------- #
# LIST
# ---------------------------------------------------------------------- #
@router.get(
    "/list",
    summary="List locals with filters and pagination",
    response_model=list[LocalView],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Locals listed successfully."},
        404: {"description": "No locals found."},
    },
)
# @cached_json("list", ttl=86400)              # ???  24 h _a “mágica” está aqui_
def list_locals(
    request: Request,
    filters: Annotated[LocalFilters, Depends()],
    service: LocalService = _provide_local_service,
) -> list[LocalView]:
    """
    Return a paginated slice of locals, optionally filtered by any field.

    This endpoint exposes the internal Local records that the event system
    is using. These records can come from the internal LocalInfo API or be
    manually created/edited as a fallback when that API is unavailable or
    outdated.
    
    The query parameters are mapped into a `LocalFilters` DTO, which is
    shared between controller and service. At runtime we also log warnings
    if there is any mismatch between:
    - Query parameters declared in this endpoint.
    - Fields defined in `LocalFilters`.
    """
    filter_model = from_local_filters(filters)
    
    logger.info("Local list query started", filters=filter_model)
    
    locals_ = service.list_locals(filters=filter_model)

    if not locals_:
        raise_http(logger.warning, 404, "No locals found", filters=filter_model)

    return [to_local_view(local) for local in locals_]
    


# ---------------------------------------------------------------------- #
# GET BY ID
# ---------------------------------------------------------------------- #
@router.get(
    "/by-id/{local_id}",
    summary="Get a local by ID",
    response_model=LocalView,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Local found."},
        404: {"description": "Local not found."},
    },
)
def get_local_by_id(
    local_id: int,
    service: LocalService = _provide_local_service,
) -> LocalView:
    """
    Retrieve a single Local record by its ID.
    """
    logger.info("Local query by ID", local_id=local_id)

    local = service.get_local(local_id)
    if not local:
        raise_http(logger.warning, 404, "Local not found", local_id=local_id)

    return to_local_view(local)


# ---------------------------------------------------------------------- #
# CREATE
# ---------------------------------------------------------------------- #
@router.post(
    "/create-local",
    summary="Create a new local (manual override)",
    response_model=LocalView,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    status_code=201,
    responses={
        201: {"description": "Local successfully created."},
        409: {"description": "A Local with the same name, venue type and address already exists."},
    },
)
def post_create_local(
    payload: LocalCreate,
    service: LocalService = _provide_local_service,
) -> LocalView:
    """
    Create a new Local record.

    This endpoint is used when:
    - The internal LocalInfo API is unavailable or outdated.
    - A venue does not exist yet in the internal system.
    - You need to manually register a local to be used by events.

    Every Local created here is considered a manual override.
    """
    logger.info(
        "Received request to create local",
        name=payload.name,
        venue_type=str(payload.venue_type) if payload.venue_type else None,
        capacity=payload.capacity,
        city=payload.address_city,
        state=payload.address_state,
    )

    try:
        local = service.create_local(payload)
    except DuplicateLocalError as exc:
        raise_http(
            logger.warning,
            409,
            str(exc),
            name=payload.name,
            venue_type=str(payload.venue_type) if payload.venue_type else None,
            city=payload.address_city,
            state=payload.address_state,
        )


    return to_local_view(local)


# ---------------------------------------------------------------------- #
# PATCH /update/by-id/{local_id}
# ---------------------------------------------------------------------- #
@router.patch(
    "/update/by-id/{local_id}",
    summary="Partially update a local (manual override)",
    response_model=LocalView,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Local successfully updated."},
        404: {"description": "Local not found."},
        409: {"description": "Another Local with the same name, venue type and address already exists."},
        422: {"description": "Validation error on input data."},
    },
)
def patch_local(
    local_id: int,
    payload: LocalUpdate,
    service: LocalService = _provide_local_service,
) -> LocalView:
    """
    Partially update an existing Local.

    Any update performed through this endpoint turns the Local into a manual
    override, meaning that automated sync from the internal LocalInfo API
    should not blindly overwrite these values.
    """
    logger.info("Received partial update request for local", local_id=local_id)

    try:
        local = service.update_local(local_id, payload)
    except KeyError:
        raise_http(logger.warning, 404, "Local not found", local_id=local_id)

    return to_local_view(local)


# ---------------------------------------------------------------------- #
# BATCH CREATE
# ---------------------------------------------------------------------- #
@router.post(
    "/batch",
    summary="Create multiple locals in a single request (manual override)",
    response_model=list[LocalView],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    status_code=201,
    responses={
        201: {"description": "Locals successfully created."},
        400: {"description": "Empty list provided."},
        409: {"description": "Duplicate Local found in the batch or against existing records."},
    },
)
def post_locals_batch(
    payload: list[LocalCreate],
    service: LocalService = _provide_local_service,
) -> list[LocalView]:
    """
    Create multiple Locals in one call.

    Rules:
    - The payload must contain at least one LocalCreate.
    - The same uniqueness rule is enforced for each Local.
    - If a duplicate is found (either in the database or inside the batch),
      a 409 Conflict is returned and the batch is aborted.
    """
    logger.info("Received request to create locals in batch", quantity=len(payload))

    if not payload:
        raise_http(logger.warning, 400, "Empty list provided for batch creation")

    try:
        locals_ = service.create_locals_batch(payload)
    except DuplicateLocalError as exc:
        raise_http(
            logger.warning,
            409,
            str(exc),
        )

    return [to_local_view(local) for local in locals_]


# ---------------------------------------------------------------------- #
# CSV UPLOAD
# ---------------------------------------------------------------------- #
@router.post(
    "/upload",
    summary="Create locals from a CSV file (manual override)",
    response_model=dict,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    status_code=201,
    responses={
        201: {"description": "Locals successfully imported."},
        400: {"description": "Invalid file or no locals imported."},
    },
)
async def upload_locals_csv(
    file: UploadFile = File(...),
    service: LocalService = _provide_local_service,
) -> dict:
    """
    Import Local records from a CSV file.

    Expected CSV columns:
    - location_name (required)
    - capacity (required, integer)
    - venue_type (optional, matches the VenueType enum value)
    - is_accessible (optional, truthy string like 'true', '1', 'yes')
    - address (optional)
    - external_id
    - source
    - is_indoor
    - has_cover
    - capacity_seated
    - capacity_standing
    - latitude
    - longitude
    - timezone

    Rules:
    - Rows that cannot be parsed are logged and counted as errors.
    - Rows that would create a duplicate Local are logged and counted
      as duplicates.
    - If no valid Local is imported, a 400 error is returned.
    """
    content = await file.read()
    try:
        decoded = content.decode("utf-8")
    except UnicodeDecodeError:
        raise_http(
            logger.error,
            400,
            "Error decoding CSV file. Make sure it is encoded in UTF-8.",
        )

    reader = csv.DictReader(StringIO(decoded))

    total_rows = 0
    imported = 0
    duplicates = 0
    errors = 0

    for idx, row in enumerate(reader, start=1):
        total_rows += 1
        try:
            csv_row = LocalCsvRow.from_csv_row(row)

            if not csv_row.name:
                raise ValueError("Missing location_name")

            payload = from_local_csv_row(csv_row)

            service.create_local(payload)
            imported += 1

        except DuplicateLocalError as exc:
            logger.warning(
                "Duplicate Local found in CSV row",
                line=idx,
                reason=str(exc),
                row=row,
            )
            duplicates += 1
        except Exception as e:
            logger.exception("Error on CSV line %s: %s", idx, e)
            errors += 1

    if imported == 0:
        raise_http(
            logger.warning,
            400,
            "No valid locals were imported from CSV",
            total_rows=total_rows,
            duplicates=duplicates,
            errors=errors,
        )

    logger.info(
        "Local CSV import finished",
        total_rows=total_rows,
        imported=imported,
        duplicates=duplicates,
        errors=errors,
    )

    return {
        "status": "finished",
        "total_rows": total_rows,
        "imported": imported,
        "duplicates": duplicates,
        "errors": errors,
    }


# ---------------------------------------------------------------------- #
# DELETE /delete/by-id/{local_id}
# ---------------------------------------------------------------------- #
@router.delete(
    "/delete/by-id/{local_id}",
    summary="Delete a local by ID",
    response_model=dict,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Local successfully removed."},
        404: {"description": "Local not found."},
    },
)
def delete_local(
    local_id: int,
    service: LocalService = _provide_local_service,
) -> dict[str, str]:
    """
    Delete a Local record from the internal system.
    """
    logger.info("Received request to delete local", local_id=local_id)

    try:
        service.delete_local(local_id)
    except KeyError:
        raise_http(logger.warning, 404, "Local not found", local_id=local_id)

    logger.info("Local successfully removed", local_id=local_id)
    return {"message": f"Local with ID {local_id} successfully removed."}


# ---------------------------------------------------------------------- #
# DOWNLOAD ALL LOCALS
# ---------------------------------------------------------------------- #
@router.get(
    "/download",
    summary="Download all registered locals",
    response_model=list[LocalView],
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        200: {"description": "Local list successfully returned."},
        404: {"description": "No locals found."},
    },
)
def download_locals(
    service: LocalService = _provide_local_service,
):
    """
    Return all Local records registered in the system, without pagination.

    This is intended for:
    - Full exports (e.g., backup or synchronization).
    - Debugging and administration tools.
    - Offline analysis of all known venues.

    Returns:
        A list of `LocalView` representing all persisted locals.

    Raises:
        HTTPException(404): If no locals are found.
    """
    logger.info("Download of all locals requested")

    locals_ = service.list_all_locals()

    if not locals_:
        raise_http(logger.warning, 404, "No locals found")

    payload = [to_local_view(local) for local in locals_]

    # Force JSON encoding to avoid issues with non-serializable types
    return JSONResponse(content=jsonable_encoder(payload))


@router.get(
    "/conflicts",
    summary="List groups of locals that are probably duplicates",
    response_model=list[LocalConflictGroup],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={200: {"description": "Conflicting locals returned."}},
)
def get_local_conflicts(
    service: LocalService = _provide_local_service,
) -> list[LocalConflictGroup]:
    """
    Return groups of Locals that are likely duplicates according to
    the same normalization used to enforce uniqueness on creation.

    Each group contains at least two Locals.
    """
    groups = service.find_conflicting_locals()

    return [
        LocalConflictGroup(
            conflict_key=service._build_conflict_key(group[0]),  # type: ignore[attr-defined]
            locals=[LocalView.model_validate(local) for local in group],
        )
        for group in groups
    ]


@router.post(
    "/merge",
    summary="Merge several Locals into a single target local",
    response_model=LocalView,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Locals merged successfully."},
        400: {"description": "Invalid merge request."},
        404: {"description": "Target or source Local not found."},
    },
)
def post_merge_locals(
    payload: LocalMergeRequest,
    service: LocalService = _provide_local_service,
) -> LocalView:
    """
    Merge multiple Locals into a single target Local.

    This operation currently only deletes the source Locals and keeps
    the target intact. It does not yet update Events or other references.
    """
    try:
        merged = service.merge_locals(
            target_id=payload.target_id,
            source_ids=payload.source_ids,
        )
    except ValueError as exc:
        raise_http(logger.warning, 400, str(exc))
    except KeyError as exc:
        raise_http(logger.warning, 404, str(exc))

    return LocalView.model_validate(merged)


# # ---------------------------------------------------------------------- #
# # PATCH /{event_id}/local
# # ---------------------------------------------------------------------- #
# @router.patch(
#     "/{event_id}/local",
#     summary="Update the local associated with an event (manual override)",
#     response_model=LocalView,
#     dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
#     responses={
#         200: {"description": "Event local information successfully updated."},
#         404: {"description": "Event or local not found."},
#         422: {"description": "Invalid or empty payload."},
#     },
# )
# def patch_event_by_id_local_info( #async?
#     # background_tasks: BackgroundTasks,
#     event_id: int,
#     update: LocalUpdate | None = Body(None),
#     local_service: LocalService = _provide_local_service,
#     event_service: EventService = _provide_event_service,
# ) -> LocalView:
#     """
#     Update the Local entity associated with a given Event.

#     Rules:
#     - If the payload is `null`, returns 422.
#     - If the event does not exist, returns 404.
#     - If the event has no `local_id`, returns 404 indicating that there is
#       no local associated.
#     - Otherwise, applies a partial update on the Local via LocalService.

#     Any change performed through this endpoint is considered a manual override
#     of the local information for that event.
#     """
#     if update is None:
#         raise_http(logger.warning, 422, "Invalid Local payload (null received)")

#     logger.info("Request to update event's local received", event_id=event_id)

#     event = event_service.get_event(event_id)
#     if not event:
#         raise_http(logger.warning, 404, "Event not found", event_id=event_id)

#     if event.local_id is None:
#         raise_http(
#             logger.warning,
#             404,
#             "Event has no local associated",
#             event_id=event_id,
#         )

#     try:
#         local = local_service.update_local(event.local_id, update)
#     except KeyError:
#         # caso o local_id do evento aponte para um Local inexistente
#         raise_http(
#             logger.warning,
#             404,
#             "Associated Local not found",
#             event_id=event_id,
#             local_id=event.local_id,
#         )

#     logger.info(
#         "Event local updated successfully",
#         event_id=event_id,
#         local_id=local.id,
#     )

#     return LocalView(
#         id=local.id,  # type: ignore[arg-type]
#         location_name=local.location_name,
#         capacity=local.capacity,
#         venue_type=local.venue_type,
#         is_accessible=local.is_accessible,
#         address=local.address,
#         manually_edited=local.manually_edited,
#         created_at=local.created_at,
#         updated_at=local.updated_at,
#     )
