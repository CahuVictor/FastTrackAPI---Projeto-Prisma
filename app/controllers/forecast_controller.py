# app/controllers/event_controller.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Body, UploadFile, File, BackgroundTasks, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timezone
from structlog import get_logger
from io import StringIO
import inspect
import csv
import asyncio
import json

from app.core.rate_limit_config import limiter
from app.core.deps import provide_event_repo, provide_event_service, provide_local_service, provide_forecast_service
from app.schemas.forecast.forecast_create import ForecastCreate
from app.schemas.forecast.forecast_update import ForecastUpdate
from app.schemas.forecast.forecast_view import ForecastView
from app.models.forecast import Forecast
from app.schemas.common import MessageResponse
from app.services.forecast_service import ForecastService
from app.utils.http import raise_http

_provide_forecast_service = Depends(provide_forecast_service)

logger = get_logger().bind(module="forecast")

router = APIRouter(
    prefix="/forecast",
    tags=["forecast"],
#     dependencies=[auth_dep]
)

@router.get(
    "/forecast_info",
    summary="Busca previsão do tempo para uma cidade e data/hora (mock)",
    response_model=MessageResponse,
    # dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Previsão recebida"},
        404: {"description": "Previsão não recebida"}
    },
)
@cached_json("forecast", ttl=1800)              # ⬅⬅️ _a “mágica” está aqui_
async def get_forecast_info(
    # background_tasks: BackgroundTasks,
    city: str = Query(..., description="Nome da cidade"),
    date: datetime = Query(..., description="Data e hora de referência para a previsão"),
):
    """
    Retorna a previsão do tempo simulada para a cidade e data/hora informadas.
    Cache: 30 min (1800 s)
    """
    logger.info("Consulta de clima iniciada", city=city, date=date)
    # Adiciona task em background para buscar forecast depois
    # background_tasks.add_task(
    #     atualizar_forecast_em_background,
    #     event_resp.id
    # )
    
    # TODO
    
    # Essa função deve retornar o forecast para um range de horários no dia solicitado
    # Pode-se pensar em pegar para dias tbm
    
    logger.info("Endpoint em construção")
    return {"detail": "Endpoint em construção"}

@router.patch(
    "/{event_id}/forecast_info",
    summary="Atualiza a previsão do tempo de um evento.",
    response_model=MessageResponse,
    # dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Previsão do tempo atualizada com sucesso."},
        404: {"description": "Evento não encontrado."},
        502: {"description": "Erro ao obter previsão do tempo"}
    },
)
def patch_event_by_id_forecast_info(
    # background_tasks: BackgroundTasks,
    event_id: int,
    repo: ForecastService = _provide_forecast_service,
) -> dict:
    """
    Aciona a tarefa de reprocessamento do forecast do evento.
    """
    logger.info("Requisição para reprocessar forecast_info recebida", event_id=event_id)
    
    # event = repo.get(event_id)
    # if event is None:
    #     raise_http(logger.warning, 404, "Evento não encontrado", event_id=event_id)
    # assert event is not None  # MyPy entende que daqui pra frente não é mais None
    
    # # Adiciona task em background para buscar forecast depois
    # background_tasks.add_task(
    #     atualizar_forecast_em_background,
    #     event_id
    # )

    # logger.info("Tarefa de atualização de forecast agendada", event_id=event_id)
    return {"detail": "Tarefa de atualização de forecast agendada"}