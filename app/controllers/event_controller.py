# app/controllers/event_controller.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Body, UploadFile, File, BackgroundTasks, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from datetime import datetime, timezone
from structlog import get_logger
from io import StringIO
import inspect
import csv
import asyncio
import json

from app.core.rate_limit_config import limiter

from app.core.deps import provide_event_service, provide_local_service
from app.schemas.event.event_create import EventCreate
from app.schemas.event.event_update import EventUpdate
from app.schemas.event.event_view import EventView
from app.models.event import Event
from app.schemas.common import MessageResponse
from app.services.event_service import EventService

from app.infra.cache.cache import cached_json
from app.utils.http import raise_http
# from app.utils.patch import update_event, should_update_forecast
from app.utils.security import require_roles, auth_dep # TODO Utilizar auth_service

# # from app.services.forecast import atualizar_forecast_em_background

# WebSocket notifications
from app.infra.websockets.ws_events import (
    notify_upload_progress, notify_upload_error, notify_upload_end,
    notify_event_created, notify_replace_started, notify_replace_done,
    notify_event_viewed_update, notify_top_viewed_update
)
from app.infra.websockets.ws_dashboard import notify_user_count

_provide_event_service = Depends(provide_event_service)
_provide_local_service = Depends(provide_local_service)
# _provide_forecast_service = Depends(provide_forecast_service)

logger = get_logger().bind(module="eventos")

router = APIRouter(
    prefix="/events",
    tags=["events"],
    # dependencies=[auth_dep]
)


# ------------------------------------------------------------------ #
# Helper methods for common actions
# ------------------------------------------------------------------ #
def _to_event_view(event: Event) -> EventView:
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
        city=event.city,
        age_restriction=event.age_restriction,
        participants=event.participants,
        views=event.views,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )
    
def _from_event_view(view: EventView) -> Event:
    """
    Map an `EventView` schema into a domain `Event` entity.

    This helper is intended for specific use cases where the API needs to
    accept a full event representation (e.g., replace endpoints) and
    convert it back into the domain model.

    Important:
        - The `id` field is intentionally set to `None` here; the service
          layer is responsible for enforcing or overriding the actual ID.
        - Audit-related fields such as `created_at` and `updated_at`
          should normally be controlled by the repository / infrastructure
          layer and not blindly trusted from the client.

    Args:
        view: An `EventView` instance received from the API layer.

    Returns:
        A domain `Event` entity built from the given view.
    """
    return Event(
        # id=None,  # ID will be enforced by the service/repository layer.
        title=view.title,
        description=view.description,
        status=view.status,
        start_time=view.start_time,
        end_time=view.end_time,
        timezone=view.timezone,
        city=view.city,
        age_restriction=view.age_restriction,
        participants=view.participants,
        # views=view.views,
        # created_at=view.created_at,
        # updated_at=view.updated_at,
    )


# ----------------------------------------------------------------------
# LIST
# ----------------------------------------------------------------------
@router.get(
    "/list",
    summary="List events with filters and pagination",
    response_model=list[EventView],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
)
@limiter.limit("60/minute")
def list_events(
    request: Request,  # ? Necessário para funcionar com @limiter.limit,
    skip: int = Query(0, ge=0, description="How many records to skip"), # "Quantos registros pular"),
    limit: int = Query(20, le=100, description="Page size"), # "Tamanho da página"),
    city: str | None = Query(None, description="Filter by city"), # "Filtrar por cidade"),
    service: EventService = _provide_event_service,
) -> list[EventView]:
    """
    Return a paginated slice of events, optionally filtered by city.

    Args:
        request: Incoming HTTP request (required by the rate limiter).
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.
        city: Optional city name to filter events.

    Returns:
        A list of `EventView` objects representing the events found.

    Raises:
        HTTPException(404): If no events are found.
    """
    logger.info("Event list query started", skip=skip, limit=limit, city=city)

    events = service.list_events(skip=skip, limit=limit, city=city)

    if not events:
        raise_http(logger.warning, 404, "No events found", skip=skip, limit=limit, city=city)

    return [_to_event_view(event) for event in events]


# ----------------------------------------------------------------------
# GET BY ID + increment views
# ----------------------------------------------------------------------
@router.get(
    "/by-id/{event_id}",
    summary="Get an event by ID and increment views",
    response_model=EventView,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Event found."},
        404: {"description": "Event not found."},
    },
)
@limiter.limit("60/minute")
async def get_event_by_id(
    request: Request,  # ? Necessário para funcionar com @limiter.limit,
    # background_tasks: BackgroundTasks,
    event_id: int,
    service: EventService = _provide_event_service,
) -> EventView:
    """
    Retrieve a single event by its unique identifier and increment its
    view counter.

    Args:
        request: Incoming HTTP request (required by the rate limiter).
        event_id: Unique identifier of the event.

    Returns:
        An `EventView` with the updated number of views.

    Raises:
        HTTPException(404): If the event is not found.
    """
    logger.info("Event query by ID", event_id=event_id)

    try:
        event = service.view_event(event_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Event not found")

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        raise_http(logger.warning, 404, "Event not found", event_id=event_id)
    assert event is not None  # MyPy entende que daqui pra frente não é mais None

    return _to_event_view(event)


# ----------------------------------------------------------------------
# CREATE
# ----------------------------------------------------------------------
@router.post(
    "/create-event",
    summary="Create a new event",
    response_model=EventView,
    status_code=201,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={201: {"description": "Event successfully created."}},
)
# async def post_create_event(
def post_create_event(
    # background_tasks: BackgroundTasks,
    payload: EventCreate,
    service: EventService = _provide_event_service,
) -> EventView:
    """
    Create a new event and return the persisted data.

    Args:
        payload: `EventCreate` payload with the event data.

    Returns:
        An `EventView` instance representing the created event.
    """
    logger.info("Received request to create event", title=payload.title, city=payload.city, start_time=payload.start_time, end_time=payload.end_time,)

    event = service.create_event(payload, changed_by="anonymous")

    return _to_event_view(event)


# ----------------------------------------------------------------------
# PUT /replace (replace ALL)
# ----------------------------------------------------------------------
@router.put(
    "/replace",
    summary="Replace all existing events with a new list",
    response_model=list[EventView],
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        200: {"description": "All events have been replaced successfully."},
        400: {"description": "Invalid list sent."},
    },
)
async def put_events(
    events_new: list[EventCreate],
    service: EventService = _provide_event_service,
) -> list[EventView]:
    """
    Replace the entire collection of events with a new list.

    Args:
        events_new: List of `EventCreate` payloads representing the new
            state of the events collection.

    Returns:
        A list of `EventView` representing the persisted events after
        the replacement operation.

    Raises:
        HTTPException(400): If an empty list is provided.
    """
    logger.info("Received request to replace all events", quantity=len(events_new))

    if not events_new:
        raise_http(logger.warning, 400, "Empty list provided")

    asyncio.create_task(notify_replace_started())

    # Convert input schemas to domain entities
    domain_events: List[Event] = [_from_event_view(event) for event in events_new]

    events = service.replace_all_events(domain_events, changed_by="anonymous")

    asyncio.create_task(notify_replace_done())
    asyncio.create_task(notify_user_count())
    logger.info("All events have been successfully replaced", total=len(events))

    return [_to_event_view(event) for event in events]


# ----------------------------------------------------------------------
# PUT /replace/by-id/{event_id} (replace by ID)
# ----------------------------------------------------------------------
@router.put(
    "/replace/by-id/{event_id}",
    summary="Replace an existing event by ID",
    response_model=EventView,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Event successfully replaced."},
        404: {"description": "Event not found."},
    },
)
def put_event_by_id(
    event_id: int,
    new_event: EventView,
    service: EventService = _provide_event_service,
) -> EventView:
    """
    Fully replace the data of an existing event by ID.

    Args:
        event_id: Identifier of the event to be replaced.
        new_event: Complete event data in `EventView` format.

    Returns:
        An `EventView` representing the persisted event.

    Raises:
        HTTPException(404): If the event is not found.
    """
    logger.info("Received request to replace event by ID", event_id=event_id)

    domain_event = _from_event_view(new_event)

    try:
        event = service.replace_event_by_id(event_id, domain_event, changed_by="anonymous")
    except KeyError:
        raise HTTPException(status_code=404, detail="Event not found")

    logger.info("Event successfully replaced", event_id=event_id)

    return _to_event_view(event)

# @router.delete(
#     "/",
#     summary="Remove todos os eventos cadastrados.",
#     response_model=dict,
#     dependencies=[auth_dep, Depends(require_roles("admin"))],
#     responses={
#         200: {"description": "Todos os eventos removidos com sucesso."},
#         400: {"description": "Não foi possível remover os eventos."}
#     },
# )
# def delete_events(
#                                 repo: AbstractEventRepo = _provide_event_repo
#     ) -> dict[str, str]:
#     """
#     Apaga todos os eventos registrados.
#     """
#     logger.info("Requisição para deletar todos os eventos recebida")
#     try:
#         repo.delete_all()
#         logger.info("Todos os eventos foram removidos com sucesso")
#         return {"mensagem": "Todos os eventos foram apagados com sucesso."}
#     except Exception as e:
#         raise_http(logger.error, 400, "Erro ao tentar remover todos os eventos", error=str(e))
#     raise

# ----------------------------------------------------------------------
# DELETE /delete/by-id/{event_id}
# ----------------------------------------------------------------------
@router.delete(
    "/delete/by-id/{event_id}",
    summary="Delete a specific event by ID",
    response_model=dict,
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        200: {"description": "Event successfully removed."},
        404: {"description": "Event not found."},
    },
	# status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event(
    event_id: int,
    service: EventService = _provide_event_service,
) -> dict[str, str]:
    """
    Remove a single event by its ID.

    Args:
        event_id: Identifier of the event to be removed.

    Returns:
        A simple JSON message indicating successful deletion.

    Raises:
        HTTPException(404): If the event is not found.
    """
    logger.info("Received request to delete event", event_id=event_id)

    try:
        service.delete_event(event_id, changed_by="anonymous")
    except KeyError:
        raise HTTPException(status_code=404, detail="Event not found")

    logger.info("Event successfully removed", event_id=event_id)
    return {"message": f"Event with ID {event_id} successfully removed."} # f"Evento com ID {event_id} removido com sucesso."}


# ----------------------------------------------------------------------
# PATCH /update/by-id/{event_id}
# ----------------------------------------------------------------------
@router.patch(
    "/update/by-id/{event_id}",
    summary="Partially update event information",
    response_model=EventView,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Event successfully updated."},
        400: {"description": "No valid field provided for update."},
        404: {"description": "Event not found."},
        422: {"description": "Validation error on input data."},
    },
)
def patch_event(
    # background_tasks: BackgroundTasks,
    event_id: int,
    payload: EventUpdate,
    service: EventService = _provide_event_service,
) -> EventView:
    """
    Partially update the event with the given ID. Only the fields explicitly
    provided in the payload will be modified.

    Args:
        event_id: Identifier of the event to be updated.
        payload: `EventUpdate` payload with optional fields to patch.

    Returns:
        An `EventView` representing the updated event.

    Raises:
        HTTPException(404): If the event is not found.
    """
    logger.info("Received partial update request", event_id=event_id)

    try:
        event = service.update_event(event_id, payload, changed_by="anonymous")
    except KeyError:
        raise HTTPException(status_code=404, detail="Event not found")

    return _to_event_view(event)


# ----------------------------------------------------------------------
# DOWNLOAD ALL EVENTS
# ----------------------------------------------------------------------
@router.get(
    "/download",
    summary="Download all registered events",
    response_model=list[EventView],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Event list successfully returned."},
        404: {"description": "No events found."},
    },
)
@limiter.limit("5/minute")
def download_events(
    request: Request,  # ? Necessário para funcionar com @limiter.limit,
    service: EventService = _provide_event_service,
):
    """
    Return all events registered in the system, without pagination.

    Returns:
        A list of `EventView` with all persisted events.

    Raises:
        HTTPException(404): If no events are found.
    """
    logger.info("Download of all events requested")

    events = service.list_all_events()

    if not events:
        raise_http(logger.warning, 404, "No events found")

    payload = [_to_event_view(event) for event in events]
    
    # Se você quiser forçar JSONResponse com jsonable_encoder:
    return JSONResponse(content=jsonable_encoder(payload))
    # return payload

# ----------------------------------------------------------------------
# TOP SOON
# ----------------------------------------------------------------------
@router.get(
    "/top/soon",
    summary="Get the soonest upcoming events",
    response_model=list[EventView],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "List of upcoming events."},
        404: {"description": "No future events found."},
    },
)
@cached_json("top-soon", ttl=10)  # snapshot curto (10 s)
async def get_events_top_soon(
    limit: int = Query(10, ge=1, le=50, description="How many events to return"), # "Quantos eventos retornar"),
    service: EventService = _provide_event_service,
) -> list[EventView]:
    """
    Return the `limit` future events whose dates are closest to the
    current time.

    Args:
        limit: Maximum number of events to return.

    Returns:
        A list of `EventView` objects sorted by `event_date` ascending.

    Raises:
        HTTPException(404): If there are no future events.
    """
    logger.info("Query for soonest events started", limit=limit)

    most_soon = service.get_top_soon_events(limit=limit)

    if not most_soon:
        raise_http(logger.warning, 404, "No future events found", limit=limit)

    logger.info("Query for soonest events finished", quantity=len(most_soon))

    return [_to_event_view(event) for event in most_soon]


# ----------------------------------------------------------------------
# TOP MOST VIEWED
# ----------------------------------------------------------------------
@router.get(
    "/top/most-viewed",
    summary="Get the most viewed events",
    response_model=list[EventView],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "List of most viewed events."},
        404: {"description": "No events found."},
    },
)
@cached_json("top-viewed", ttl=30)  # 30 s é suficiente p/ ranking
async def get_events_top_viewed(
    limit: int = Query(10, ge=1, le=50),
    service: EventService = _provide_event_service,
) -> list[EventView]:
    """
    Return the `limit` events with the highest view count. Ties are
    resolved by event date (closest date first).

    Args:
        limit: Maximum number of events to return.

    Returns:
        A list of `EventView` ordered by popularity.

    Raises:
        HTTPException(404): If there are no events.
    """
    logger.info("Query for most viewed events started", limit=limit)

    most_viewed = service.get_top_viewed_events(limit=limit)

    if not most_viewed:
        raise_http(logger.warning, 404, "No events found", limit=limit)

    # Notify via WebSocket (only titles for the dashboard)
    asyncio.create_task(
        notify_top_viewed_update([e.title for e in most_viewed])
    )

    logger.info("Query for most viewed events finished", quantity=len(most_viewed))

    return [_to_event_view(event) for event in most_viewed]


# ----------------------------------------------------------------------
# BATCH CREATE (POST /lote)
# ----------------------------------------------------------------------
@router.post(
    "/lote",
    summary="Adiciona uma lista de novos eventos, atribuindo novos IDs.",
    response_model=list[EventView],
    status_code=201,
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        201: {"description": "Eventos adicionados com sucesso."},
        400: {"description": "Lista inválida enviada."},
    },
)
async def post_events_batch(
    # background_tasks: BackgroundTasks,
    events: list[EventCreate],
    service: EventService = _provide_event_service,
) -> list[EventView]:
    """
    Create multiple events at once, each receiving a new ID.

    Args:
        events: List of `EventCreate` payloads with event data.

    Returns:
        A list of `EventView` representing the newly created events.

    Raises:
        HTTPException(400): If an empty list is provided.
    """
    logger.info("Received request to create events in batch", quantity=len(events))

    if not events:
        raise_http(logger.warning, 400, "Empty list provided")

    created_events = service.create_events_batch(events, changed_by="anonymous")

    # Aqui você poderia adicionar tasks de forecast em background se tiver
    # uma função do tipo `atualizar_forecast_em_background`.
    # for ev in created_events:
    #     background_tasks.add_task(atualizar_forecast_em_background, ev.id)

    # Notificações por WebSocket (progresso)
    new_events = 0
    for ev in created_events:
        await notify_upload_progress(ev.title)
        new_events += 1

    logger.info("Batch events successfully created", total_created=new_events)
    await notify_upload_end(len(created_events))
    await notify_user_count()

    return [_to_event_view(event) for event in created_events]


# ----------------------------------------------------------------------
# CSV UPLOAD
# ----------------------------------------------------------------------
@router.post(
    "/upload",
    summary="Create events from a CSV file",
    response_model=dict,
    status_code=201,
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        201: {"description": "Events successfully imported."},
        400: {"description": "Invalid file or no events imported."},
    },
)
# @limiter.limit("20/minute")
async def upload_csv(
    # request: Request,  # ? Necessário para funcionar com @limiter.limit,
    # background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    service: EventService = _provide_event_service,
) -> dict:
    """
    Import events from a CSV file and create them in the repository.

    The CSV is expected to contain at least the following columns:
        - title
        - description
        - event_date (ISO-8601 string)
        - city
        - participants (semicolon-separated list, e.g. "Ana;Bruno;Carla")

    Args:
        file: Uploaded CSV file containing event data.
        service: Event service instance injected by FastAPI.

    Returns:
        A JSON object with the status and total number of imported events.

    Raises:
        HTTPException(400): If the file cannot be decoded as UTF-8 or if
            no valid events are imported.
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

    total = 0
    created_events: List[Event] = []

    for idx, row in enumerate(reader, start=1):
        try:
            payload = EventCreate(
                title=row["title"],
                description=row["description"],
                status=row["status"],
                
                start_time=row["start_time"],
                end_time=row["end_time"],
                timezone=row["timezone"],
        
                city=row["city"],
                age_restriction=row["age_restriction"],
                
                participants=row["participants"].split(";") if row.get("participants") else [],
                # Se quiser suportar local_id/forecast_id no CSV, adiciona aqui
            )

            event = service.create_event(payload, changed_by="anonymous")
            created_events.append(event)
            total += 1
            
            # Adiciona task em background para buscar forecast depois
            # background_tasks.add_task(
            #     atualizar_forecast_em_background,
            #     event_resp.id
            # )

            await notify_upload_progress(event.title)
        except Exception as e:
            # registra no console + WebSocket
            logger.exception("Error on CSV line %s: %s", idx, e)
            await notify_upload_error(str(e))

    await notify_upload_end(len(created_events))
    await notify_user_count()

    if not created_events:
        raise_http(logger.warning, 400, "No valid events were imported")

    return {"status": "finished", "total": total}