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

# from app.core.rate_limit_config import limiter
from app.core.deps import provide_event_repo, provide_event_service, provide_local_service, provide_forecast_service
from app.schemas.local_create import LocalCreate
from app.schemas.local_update import LocalUpdate
from app.schemas.local_view import LocalView
from app.models.local import Local
from app.services.local_service import LocalService
from app.utils.http import raise_http

_provide_local_service = Depends(provide_local_service)

logger = get_logger().bind(module="local")

router = APIRouter(
    prefix="/local",
    tags=["local"],
#     dependencies=[auth_dep]
)

@router.get(
    "/local_info",
    summary="Busca informações de um local pelo nome",
    response_model=LocalView,
    # dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Local encontrado"},
        404: {"description": "Local não encontrado"}
    },
)
@cached_json("local-info", ttl=86400)              # ⬅⬅️ _a “mágica” está aqui_
async def get_local_info(
    location_name: str = Query(..., description="Nome do local a ser buscado"),
    service: LocalService = _provide_local_service,
) -> LocalView:
    """
    Retorna as informações detalhadas de um local a partir do nome.
    Cache: 24 h (86400 s)
    """
    logger.info("Consulta de local iniciada", location_name=location_name)
    
    result = None # await service.get_by_name(location_name)
    # if inspect.iscoroutine(result):
    #     result = await result
        
    if not result:
        raise_http(logger.warning, 404, "Local não encontrado", location_name=location_name)
    return result

@router.patch(
    "/{event_id}/local_info",
    summary="Atualiza informações do local de um evento.",
    response_model=LocalView,
    # dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Informações do local atualizadas com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def patch_event_by_id_local_info( #async?
    # background_tasks: BackgroundTasks,
    event_id: int,
    update: LocalUpdate | None = Body(None),
    service: LocalService = _provide_local_service,
) -> LocalView:
    """
    Atualiza o campo local_info de um evento específico.
    """
    if update is None:                       # ← trata JSON null
        raise_http(logger.warning, 422, "Erro ao receber dados do Local")
    assert update is not None # MyPy entende que daqui pra frente update não é mais None
    
    logger.info("Requisição para atualizar local_info recebida", event_id=event_id)
    event = None # repo.get(event_id)
    # if event is None:
    #     raise_http(logger.warning, 404, "Evento não encontrado", event_id=event_id)
    # assert event is not None  # MyPy entende que daqui pra frente event não é mais None
    
    # update_event(event, update, attr="local_info")
    
    # # TODO verificar se ao mudar o local info, também foi alterada a cidade
    
    # if event.city or event.event_date:
    #     # Adiciona task em background para buscar forecast depois
    #     background_tasks.add_task(
    #         atualizar_forecast_em_background,
    #         event_id
    #     )
    
    # logger.info("Informações do local atualizadas com sucesso", event_id=event_id)
    # return repo.replace_by_id(event_id, event)