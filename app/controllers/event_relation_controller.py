# app/controllers/event_relation_controller.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from structlog import get_logger

from app.core.deps import provide_event_service, provide_local_service  # ajuste se o nome for diferente
from app.schemas.local.local_view import LocalView
from app.schemas.common.common import MessageResponse
from app.services.event_service import EventService
from app.services.local_service import LocalService  # certifique-se que existe este service
# from app.services.forecast_service import ForecastService  # <- descomente quando existir
# from app.core.deps import provide_forecast_service
from app.utils.security import require_roles, auth_dep

_provide_event_service = Depends(provide_event_service)
_provide_local_service = Depends(provide_local_service)

logger = get_logger().bind(module="event_relations")

router = APIRouter(
    prefix="/events",
    tags=["event-relations (Not Implemented)"],
)


# ----------------------------------------------------------------------
# Schemas de apoio (request)
# ----------------------------------------------------------------------
from pydantic import BaseModel, Field


class EventLocalLinkRequest(BaseModel):
    """
    Payload used when associating an Event with a Local.

    This payload is meant to carry metadata related to the link itself
    (for example, who is performing the operation or a comment).
    It does NOT represent the Local entity, only the relationship.
    """
    source: Optional[str] = Field(
        default=None,
        description=(
            "Optional source/origin of this association "
            "(e.g. 'manual', 'sync', 'import')."
        ),
        examples=["manual", "internal_sync"],
    )
    comment: Optional[str] = Field(
        default=None,
        description="Optional free-text comment about this association.",
        examples=["Primary venue for the opening night."],
    )


class EventForecastLinkRequest(BaseModel):
    """
    Payload used to link an Event with a Forecast entry based on
    spatial (lat/lon) and temporal information.

    The idea is that a service will use this information to resolve the
    appropriate forecast record and attach it to the event.
    """
    latitude: float = Field(
        description="Latitude of the event location in decimal degrees.",
        examples=[-8.0476],
    )
    longitude: float = Field(
        description="Longitude of the event location in decimal degrees.",
        examples=[-34.8770],
    )
    start_time: datetime = Field(
        description="Event start time (timezone-aware ISO-8601).",
        examples=["2026-03-10T10:30:00Z"],
    )
    end_time: datetime = Field(
        description="Event end time (timezone-aware ISO-8601).",
        examples=["2026-03-10T12:30:00Z"],
    )
    timezone: Optional[str] = Field(
        default=None,
        description=(
            "Optional IANA timezone identifier (e.g. 'America/Recife'). "
            "If omitted, the backend may infer or default to UTC."
        ),
        examples=["America/Recife"],
    )
    # Opcional: permitir forçar um forecast_id já conhecido
    forecast_id: Optional[int] = Field(
        default=None,
        description=(
            "Optional forecast identifier to be explicitly attached. "
            "If not provided, the service is expected to resolve the "
            "forecast from latitude/longitude and time interval."
        ),
        examples=[42],
    )


# ----------------------------------------------------------------------
# POST /{event_id}/attach-local/{local_id}
# ----------------------------------------------------------------------
@router.post(
    "/{event_id}/attach-local/{local_id}",
    summary="Attach an existing local to an event",
    response_model=MessageResponse,
    responses={
        200: {"description": "Event successfully associated with the given Local."},
        404: {"description": "Event or Local not found."},
    },
)
def attach_local_to_event(
    event_id: int,
    local_id: int,
    payload: EventLocalLinkRequest = Body(
        default_factory=EventLocalLinkRequest,
        description="Optional metadata about this association.",
    ),
    event_service: EventService = _provide_event_service,
    local_service: LocalService = _provide_local_service,
) -> dict[str, str]: # MessageResponse:
    """
    Attach an existing Local to an Event.

    This endpoint is responsible for the *relationship* between Event
    and Local, and should be the single entry point for this operation
    at the HTTP layer.

    Current behavior:
        * Validates that the event exists.
        * Validates that the local exists.
        * Delegates the association to the service layer
          (e.g. by updating the Event or inserting into an
          `EventVenueHistory` table, depending on your model).

    Notes:
        - The exact persistence strategy (direct FK, history table, etc.)
          is intentionally abstracted behind the service layer so that we
          can evolve the schema without changing the endpoint contract.
    
    Rules:
    - 404 if the event does not exist.
    - 404 if the local does not exist.
    - Otherwise, updates `event.local_id` and persists the change.
    """
    logger.info(
        "Attach local to event requested",
        event_id=event_id,
        local_id=local_id,
        source=payload.source,
    )

    # 1) Ensure event exists
    event = event_service.get_event(event_id)
    if not event:
        logger.warning("Event not found while trying to attach local", event_id=event_id)
        raise_http(logger.warning, 404, "Event not found", event_id=event_id)

    # 2) Ensure local exists
    local = local_service.get_local(local_id)
    if not local:
        logger.warning("Local not found while trying to attach to event", local_id=local_id)
        raise_http(logger.warning, 404, "Local not found", local_id=local_id)

    event.local_id = local_id
    event_service.update_event_entity(event, changed_by=None)  # <-- crie esse método se ainda não existir
	# 3) Delegate to the service layer
    #
    # Aqui você tem duas opções de implementação, dependendo do seu modelo:
    #
    # (a) Se ainda estiver usando `event.local_id`:
    #     event.local_id = local_id
    #     event_service.update_event_entity(event, changed_by=None)
    #
    # (b) Se já estiver usando uma tabela de histórico (`EventVenueHistoryTable`):
    #     event_service.attach_local_with_history(
    #         event_id=event_id,
    #         local_id=local_id,
    #         source=payload.source,
    #         comment=payload.comment,
    #         changed_by=None,
    #     )
    #
    # Para não quebrar nada agora, vamos deixar explícito que a
    # persistência deve ser implementada no service:

    logger.info(
        "Attach local to event - persistence not implemented yet",
        event_id=event_id,
        local_id=local_id,
    )

    # return MessageResponse(
    #     message=(
    #         f"Local {local_id} validated and ready to be attached to "
    #         f"event {event_id}. (Persistence not implemented yet.)"
    #     )
    # )
    return {"message": f"Local {local_id} attached to event {event_id}."}


# ----------------------------------------------------------------------
# POST /{event_id}/attach-forecast  (ESQUELETO)
# ----------------------------------------------------------------------
@router.post(
    "/{event_id}/attach-forecast",
    summary="(Skeleton) Attach a Forecast to an Event using coordinates and time window",
    response_model=MessageResponse,
    responses={
        200: {"description": "Forecast link request accepted (skeleton)."},
        404: {"description": "Event not found."},
        501: {"description": "Forecast linking not implemented yet."},
    },
)
def attach_forecast_to_event(
    event_id: int,
    payload: EventForecastLinkRequest,
    event_service: EventService = Depends(provide_event_service),
    # forecast_service: ForecastService = Depends(provide_forecast_service),  # <- habilitar quando existir
) -> MessageResponse:
    """
    Skeleton endpoint that will attach a Forecast entry to an Event
    based on latitude, longitude and the event's time window.

    Expected future behavior:
        1. Validate that the event exists.
        2. Either:
           - Use `payload.forecast_id`, if provided, to directly attach
             that forecast to the event; or
           - Use (latitude, longitude, start_time, end_time, timezone)
             to query the Forecast service/repository and resolve the
             best matching forecast entry.
        3. Persist the association (e.g. by setting `event.forecast_id`
           or inserting into a relation/history table).
        4. Optionally, log an audit entry indicating who performed the
           operation and which forecast was chosen.

    For now, this endpoint only validates the event and returns a
    501-style response indicating that the logic must be implemented.
    """
    logger.info(
        "Attach forecast to event requested (skeleton)",
        event_id=event_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )

    # 1) Ensure event exists
    event = event_service.get_event(event_id)
    if not event:
        logger.warning("Event not found while trying to attach forecast", event_id=event_id)
        raise HTTPException(status_code=404, detail="Event not found")

    # 2) No real forecast logic yet: this is a skeleton
    #
    # Exemplo de futura lógica (comentada):
    #
    # if payload.forecast_id is not None:
    #     forecast = forecast_service.get_forecast(payload.forecast_id)
    # else:
    #     forecast = forecast_service.find_best_forecast(
    #         lat=payload.latitude,
    #         lon=payload.longitude,
    #         start_time=payload.start_time,
    #         end_time=payload.end_time,
    #         timezone=payload.timezone,
    #     )
    #
    # event.forecast_id = forecast.id
    # event_service.update_event_entity(event, changed_by=None)
    #

    # 3) Por enquanto, apenas deixamos explícito que falta implementação
    raise HTTPException(
        status_code=501,
        detail=(
            "Forecast linking is not implemented yet. "
            "This endpoint is a skeleton and should be wired to the "
            "forecast service/repository logic."
        ),
    )


@router.get(
    "/suggestions-for-event/{event_id}",
    summary="Suggest locals for a given event",
    response_model=list[LocalView],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Suggested locals returned."},
        404: {"description": "Event not found."},
    },
)
def suggest_locals_for_event(
    event_id: int, # = Path(..., description="Event identifier"),
    max_results: int = Query(
        10, ge=1, le=50, description="Maximum number of suggestions to return"
    ),
    local_service: LocalService = _provide_local_service,
    event_service: EventService = _provide_event_service,
) -> list[LocalView]:
    """
    Suggest locals for a given event.

    Current heuristic (simple placeholder):
    - Ensures the event exists.
    - Returns up to `max_results` locals, ordered by capacity (when available)
      and location_name.

    This can be improved later to take into account city, expected audience,
    indoor/outdoor, etc.
    """
    event = event_service.get_event(event_id)
    if not event:
        raise_http(logger.warning, 404, "Event not found", event_id=event_id)

    # locals_ = local_service.list_locals(
    #     filters = LocalFilters(
    #         skip=0,
    #         limit=0,  # fetch all, we'll slice manually
    #         location_name=None,
    #         capacity=None,
    #         venue_type=None,
    #         is_accessible=None,
    #         address=None,
    #         manually_edited=None,
    #         created_at=None,
    #         updated_at=None,
    #     )
    # )

    # # simple ordering: by capacity (None last) then by name
    # locals_sorted = sorted(
    #     locals_,
    #     key=lambda l: (
    #         l.capacity is None,
    #         l.capacity if l.capacity is not None else 0,
    #         (l.name or "").lower(),
    #     ),
    # )

    # locals_sorted = locals_sorted[:max_results]

    # # return [LocalView.model_validate(local) for local in locals_sorted]
    # return [to_local_view(local) for local in locals_sorted]