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
from app.core.deps import get_event_repo # provide_local_info_service, provide_forecast_service, provide_event_repo
from app.core.deps import provide_event_repo
from app.schemas.event_create import EventCreate
from app.schemas.event_update import EventUpdate
from app.schemas.event_view import EventView
from app.models.event import Event
from app.repositories.event_repo import EventRepository
from app.schemas.common import MessageResponse

# from app.utils.cache import cached_json
# from app.utils.h_events import order_and_slice, ensure_aware
from app.utils.http import raise_http
# from app.utils.patch import update_event, should_update_forecast
# from app.utils.security import require_roles, auth_dep

# # from app.services.forecast import atualizar_forecast_em_background

# # WebSocket Notificacoes
# from app.websockets.ws_events import (
#     notify_upload_progress, notify_upload_error, notify_upload_end,
#     notify_event_created, notify_replace_started, notify_replace_done,
#     notify_event_viewed_update, notify_top_viewed_update
# )
# from app.websockets.ws_dashboard import notify_user_count

# _provide_local_info_service = Depends(provide_local_info_service)
# _provide_forecast_service = Depends(provide_forecast_service)
_provide_event_repo = Depends(provide_event_repo)

logger = get_logger().bind(module="eventos")

router = APIRouter(
    prefix="/events",
    tags=["events"],
#     dependencies=[auth_dep]
)

# @router.get(
#     "/local_info",
#     summary="Busca informações de um local pelo nome",
#     response_model=LocalInfo,
#     dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
#     responses={
#         200: {"description": "Local encontrado"},
#         404: {"description": "Local não encontrado"}
#     },
# )
# @cached_json("local-info", ttl=86400)              # ⬅⬅️ _a “mágica” está aqui_
# async def get_local_info(
#     location_name: str = Query(..., description="Nome do local a ser buscado"),
#     service: AbstractLocalInfoService = _provide_local_info_service
# ):
#     """
#     Retorna as informações detalhadas de um local a partir do nome.
#     Cache: 24 h (86400 s)
#     """
#     logger.info("Consulta de local iniciada", location_name=location_name)
    
#     result = await service.get_by_name(location_name)
#     if inspect.iscoroutine(result):
#         result = await result
        
#     if not result:
#         raise_http(logger.warning, 404, "Local não encontrado", location_name=location_name)
#     return result

# @router.get(
#     "/forecast_info",
#     summary="Busca previsão do tempo para uma cidade e data/hora (mock)",
#     response_model=MessageResponse,
#     dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
#     responses={
#         200: {"description": "Previsão recebida"},
#         404: {"description": "Previsão não recebida"}
#     },
# )
# @cached_json("forecast", ttl=1800)              # ⬅⬅️ _a “mágica” está aqui_
# async def get_forecast_info(
#     # background_tasks: BackgroundTasks,
#     city: str = Query(..., description="Nome da cidade"),
#     date: datetime = Query(..., description="Data e hora de referência para a previsão"),
# ):
#     """
#     Retorna a previsão do tempo simulada para a cidade e data/hora informadas.
#     Cache: 30 min (1800 s)
#     """
#     logger.info("Consulta de clima iniciada", city=city, date=date)
#     # Adiciona task em background para buscar forecast depois
#     # background_tasks.add_task(
#     #     atualizar_forecast_em_background,
#     #     event_resp.id
#     # )
    
#     # TODO
    
#     # Essa função deve retornar o forecast para um range de horários no dia solicitado
#     # Pode-se pensar em pegar para dias tbm
    
#     logger.info("Endpoint em construção")
#     return {"detail": "Endpoint em construção"}

# @router.get(
#     "/all",
#     deprecated=True,                                    # Marca rota como obsoleta, sem removê-la
#     include_in_schema=False,                            # Oculta rota da doc quando False
#     summary="Lista todos os eventos registrados.",
#     response_model=list[EventResponse],
#     dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
#     responses={
#         200: {"description": "Lista de eventos retornada com sucesso."},
#         404: {"description": "Nenhum evento encontrado."}
#     },
# )
# @limiter.limit("60/minute")
# def list_events_all(
#     request: Request,  # ← Necessário para funcionar com @limiter.limit,
#     repo: AbstractEventRepo = _provide_event_repo
# ) -> list[EventResponse]:
#     """
#     Retorna todos os eventos cadastrados.
#     """
#     logger.info("Consulta de todos eventos iniciada - Rota obsoleta")
#     events = repo.list_all()
    
#     if not events:
#         raise_http(logger.warning, 404, "Nenhum evento encontrado")
#     return events

# @router.get(
#     "/download",
#     summary="Download de todos os eventos registrados.",
#     response_model=list[EventResponse],
#     dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
#     responses={
#         200: {"description": "Lista de eventos retornada com sucesso."},
#         404: {"description": "Nenhum evento encontrado."}
#     },
# )
# @limiter.limit("20/minute")
# def download_eventos(
#     request: Request,  # ← Necessário para funcionar com @limiter.limit,
#     repo: AbstractEventRepo = _provide_event_repo
# ):
#     eventos = repo.list_all()
#     # return JSONResponse(content=[e.model_dump() for e in eventos])
#     # jsonable_encoder converte datetime → ISO-8601 string
#     payload = jsonable_encoder(eventos)         # <<< aqui
#     return JSONResponse(content=payload)

@router.get(
    "/",
    summary="Lista eventos com filtros e paginação",
    response_model=list[EventView],
    # dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
)
# @limiter.limit("60/minute")
def list_events(
    # request: Request,  # ← Necessário para funcionar com @limiter.limit,
    skip: int = Query(0, ge=0, description="Quantos registros pular"),
    limit: int = Query(20, le=100, description="Tamanho da página"),
    city: str | None = Query(None, description="Filtrar por cidade"),
    repo: EventRepository = _provide_event_repo, # Depends(get_event_repo),
) -> list[EventView]:
    """
    Retorna uma fatia paginada dos eventos; opcionalmente filtra por cidade.
    """
    logger.info("Consulta de evento iniciada", skip=skip, limit=limit, city=city)
    events = list(repo.list(skip=skip, limit=limit, city=city))
    if not events:
        raise_http(logger.warning, 404, "Nenhum evento encontrado", skip=skip, limit=limit, city=city)
    # return events
    return [
        EventView(
            id=e.id,  # type: ignore[arg-type]
            title=e.title,
            description=e.description,
            event_date=e.event_date,
            city=e.city,
            participants=e.participants,
            views=e.views,
            local_id=e.local_id,
            forecast_id=e.forecast_id,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
        for e in events
    ]

@router.get(
    "/{event_id}",
    summary="Obtém um evento pelo ID.",
    response_model=EventView,
    # dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Evento encontrado."},
        404: {"description": "Evento não encontrado."}
    },
)
# @limiter.limit("60/minute")
async def get_event_by_id(
    # request: Request,  # ← Necessário para funcionar com @limiter.limit,
    # background_tasks: BackgroundTasks,
    event_id: int,
    repo: EventRepository = _provide_event_repo, # Depends(get_event_repo),
) -> EventView:
    """
    Busca um evento pelo seu identificador único.
    """
    logger.info("Consulta de evento", event_id=event_id)
    event = repo.get(event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        raise_http(logger.warning, 404, "Evento não encontrado", event_id=event_id)
    assert event is not None  # MyPy entende que daqui pra frente não é mais None
    
    # if should_update_forecast(event.forecast_info):
    #     background_tasks.add_task(
    #         atualizar_forecast_em_background,
    #         event_id
    #     )
    
    event.views += 1
    logger.info("Atualizado os views", event_id=event_id, views=event.views)
    
    # Atualiza apenas o campo de visualizações
    repo.update(event) # TODO Melhor passar todos os parametros ou colocar None nos que não deveriam ser atualizados?
    
    # # Notifica via WebSocket
    # asyncio.create_task(notify_event_viewed_update(event_id, event.views))
    
    # return EventResponse.model_validate(event)
    return EventView(
        id=event.id,  # type: ignore[arg-type]
        title=event.title,
        description=event.description,
        event_date=event.event_date,
        city=event.city,
        participants=event.participants,
        views=event.views,
        local_id=event.local_id,
        forecast_id=event.forecast_id,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )

# @router.get(
#     "/top/soon",
#     summary="N eventos com data mais próxima",
#     response_model=list[EventResponse],
#     dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
#     responses={
#         200: {"description": "Lista dos eventos mais próximos."},
#         404: {"description": "Nenhum evento futuro encontrado"}
#     },
    
# )
# @cached_json("top-soon", ttl=10)  # snapshot ultra-curto (10 s)
# async def get_events_top_soon(
#     limit: int = Query(10, ge=1, le=50, description="Quantos eventos retornar"),
#     repo: AbstractEventRepo = _provide_event_repo,
# ) -> list[EventResponse]:
#     """
#     Ordena todos os eventos pelo `event_date` ascendente
#     e devolve os *limit* mais próximos da data/hora atual.
#     """
#     logger.info("Consulta de eventos mais próximos iniciada", limit=limit)
    
#     # ✅ aware - retorna um datetime aware (com fuso horário)
#     #     naive - não usar datetime naive (sem fuso horário), pois irá dificultar a ordenação depois na consulta
#     now = datetime.now(timezone.utc)

#     events = repo.list_all() # TODO Corrigir para list_partial()
#     most_soon = order_and_slice(
#         [ev for ev in events if ensure_aware(ev.event_date) >= now],
#         key_fn=lambda ev: ev.event_date,  # most soon first
#         limit=limit
#     )
    
#     if not most_soon:
#         raise_http(logger.warning, 404, "Nenhum evento futuro encontrado", limit=limit)
#     logger.info("Consulta de eventos mais próximos concluída", quantidade=len(most_soon))
#     return most_soon

# @router.get(
#     "/top/most-viewed",
#     summary="N eventos mais vistos",
#     response_model=list[EventResponse],
#     dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
#     responses={
#         200: {"description": "Lista de eventos mais vistos."},
#         404: {"description": "Nenhum evento encontrado."}
#     },
# )
# @cached_json("top-viewed", ttl=30)  # 30 s é suficiente p/ ranking
# async def get_events_top_viewed(
#     limit: int = Query(10, ge=1, le=50),
#     repo: AbstractEventRepo = _provide_event_repo,
# ) -> list[EventResponse]:
#     """
#     Retorna os *limit* eventos com maior contagem de `views`.
#     Empate é resolvido pela data do evento (mais próximo primeiro).
#     """
#     logger.info("Consulta de eventos mais vistos iniciada", limit=limit)
#     events = repo.list_all()
#     # most_viewed = (
#     #     sorted(
#     #         events,
#     #         key=lambda ev: (-ev.views, ev.event_date)  # mais views primeiro
#     #     )[:limit]
#     # )
#     most_viewed = order_and_slice(
#         events,
#         key_fn=lambda ev: (-ev.views, ev.event_date),  # most viewed first
#         limit=limit
#     )
    
#     # Notifica via WebSocket
#     asyncio.create_task(notify_top_viewed_update([e.title for e in most_viewed]))
    
#     if not most_viewed:
#         raise_http(logger.warning, 404, "Nenhum evento encontrado", limit=limit)
#     logger.info("Consulta de eventos mais vistos concluída", quantidade=len(most_viewed))
    
#     return most_viewed

@router.post(
    "/",
    summary="Cria um novo evento.",
    response_model=EventView,
    status_code=201,
    # dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        201: {"description": "Evento criado com sucesso."}
    },
)
# async def post_create_event(
def post_create_event(
    # background_tasks: BackgroundTasks,
    payload: EventCreate,
    repo: EventRepository = _provide_event_repo, # Depends(get_event_repo),
) -> EventView:
    """
    Cria um evento e tenta buscar a previsão do tempo automaticamente para preenchimento do campo forecast_info.
    Se a previsão não puder ser obtida, o evento é criado normalmente, porém forecast_info fica vazio.
    """
    logger.info("Recebida requisição para criar evento", title=payload.title, city=payload.city, event_date=payload.event_date)
    
    event = Event(
        title=payload.title,
        description=payload.description,
        event_date=payload.event_date,
        city=payload.city,
        participants=payload.participants,
        local_id=payload.local_id,
        forecast_id=payload.forecast_id,
        created_at=None,
        updated_at=None,
    )
    saved = repo.add(event)
    
    # Adiciona task em background para buscar forecast depois
    # background_tasks.add_task(
    #     atualizar_forecast_em_background,
    #     event_resp.id
    # )
    
    # # Notifica via WebSocket
    # asyncio.create_task(notify_event_created(event.title))
    # asyncio.create_task(notify_user_count())
    # logger.info("Evento criado", event_id=event_resp.id, title=event.title, city=event.city, event_date=event.event_date)
    
    # # return EventResponse.model_validate(event_resp)
    # return EventResponse.model_validate(event_resp, from_attributes=True)
    
    return EventView(
        id=saved.id,  # type: ignore[arg-type]
        title=saved.title,
        description=saved.description,
        event_date=saved.event_date,
        city=saved.city,
        participants=saved.participants,
        views=saved.views,
        local_id=saved.local_id,
        forecast_id=saved.forecast_id,
        created_at=saved.created_at,
        updated_at=saved.updated_at,
    )
    

# @router.post(
#     "/lote",
#     summary="Adiciona uma lista de novos eventos, atribuindo novos IDs.",
#     response_model=list[EventResponse],
#     status_code=201,
#     dependencies=[auth_dep, Depends(require_roles("admin"))],
#     responses={
#         201: {"description": "Eventos adicionados com sucesso."},
#         400: {"description": "Lista inválida enviada."}
#     },
# )
# async def post_events_batch(
#     background_tasks: BackgroundTasks,
#     events: list[EventCreate],
#     repo: AbstractEventRepo = _provide_event_repo,
# ) -> list[EventResponse]:
#     """
#     Cria múltiplos eventos de uma vez, atribuindo novos IDs para cada um.
#     Retorna apenas os eventos recém adicionados.
#     """
#     logger.info("Requisição para adicionar eventos em lote recebida", quantidade=len(events))
#     if not events:
#         raise_http(logger.warning, 400, "Lista vazia enviada")

#     new_events: list[EventResponse] = []
#     for event in events:

#         # Criação normal SEM forecast
#         # event_resp = repo.add(event, forecast_info=None)      # TODO
#         event_resp = repo.add(event)
        
#         # Adiciona task em background para buscar forecast depois
#         background_tasks.add_task(
#             atualizar_forecast_em_background,
#             event_resp.id
#         )
        
#         await notify_upload_progress(event.title)
#         logger.info("Evento adicionado em lote", event_id=event_resp.id, title=event.title, city=event.city, date=event.event_date)
        
#         new_events.append(event_resp)

#     logger.info("Eventos em lote adicionados com sucesso", total_adicionados=len(new_events))
#     await notify_upload_end(len(new_events))
#     await notify_user_count()
    
#     return new_events

# @router.post(
#     "/upload",
#     summary="Adiciona uma lista de novos eventos a partir de um arquivo CSV, atribuindo novos IDs.",
#     # response_model=list[EventResponse],
#     response_model=dict,
#     status_code=201,
#     dependencies=[auth_dep, Depends(require_roles("admin"))],
#     responses={
#         201: {"description": "Eventos adicionados com sucesso."},
#         400: {"description": "Lista inválida enviada."}
#     },
# )
# @limiter.limit("20/minute")
# async def upload_csv(
#     request: Request,  # ← Necessário para funcionar com @limiter.limit,
#     background_tasks: BackgroundTasks,
#     file: UploadFile = File(...),
#     repo: AbstractEventRepo = _provide_event_repo,
# ):
#     """
#     Permite o envio de um arquivo CSV com eventos e adiciona ao repositório.
#     """
#     content = await file.read()
#     try:
#         decoded = content.decode("utf-8")
#     except UnicodeDecodeError:
#         raise_http(logger.error, 400, "Erro ao decodificar o arquivo CSV. Certifique-se de que está em UTF-8.")
#     reader = csv.DictReader(StringIO(decoded))

#     new_events: list[EventResponse] = []
#     total = 0
#     # for row in reader:
#     for idx, row in enumerate(reader, start=1):
#         try:
#             event = EventCreate(
#                 title=row["title"],
#                 description=row["description"],
#                 event_date=row["event_date"],
#                 city=row["city"],
#                 participants=row["participants"].split(";"),
#                 # local_info=LocalInfo(**eval(row["local_info"]))
#                 local_info=LocalInfoResponse(**json.loads(row["local_info"]))  # 👈 mais seguro
#             )
            
#             # Criação normal SEM forecast
#             # event_resp = repo.add(event, forecast_info=None)      # TODO
#             event_resp = repo.add(event)
            
#             # Adiciona task em background para buscar forecast depois
#             background_tasks.add_task(
#                 atualizar_forecast_em_background,
#                 event_resp.id
#             )
            
#             # TODO VERIFICAR COM JOÃO SE É UMA BOA PRÁTICA
#             new_events.append(EventResponse.model_validate(event_resp))
            
#             total += 1
            
#             await notify_upload_progress(event.title)
#             # await manager.broadcast(f"✅ Evento '{evento.title}' adicionado")
#         except Exception as e:
#             # registra no console + WebSocket
#             logger.exception("Erro na linha %s do CSV: %s", idx, e)
#             await notify_upload_error(str(e))
#             # await manager.broadcast(f"❌ Erro no evento: {str(e)}")
    
#     # await manager.broadcast(f"🏁 Upload finalizado: {total} eventos adicionados")
#     await notify_upload_end(len(new_events))
#     await notify_user_count()
    
#     if not new_events:
#         raise_http(logger.warning, 400, "Nenhum evento válido foi importado")
    
#     # return new_events
#     return {"status": "finalizado", "total": total}

# @router.put(
#     "/",
#     summary="Substitui todos os eventos existentes por uma nova lista.",
#     response_model=list[EventResponse],
#     dependencies=[auth_dep, Depends(require_roles("admin"))],
#     responses={
#         200: {"description": "Todos os eventos foram substituídos."},
#         400: {"description": "Lista inválida enviada."}
#     },
# )
# def put_events(
#     events_new: list[EventResponse],
#     repo: AbstractEventRepo = _provide_event_repo,
# ) -> list[EventResponse]:
#     """
#     Substitui completamente a lista de eventos registrados.
#     """
#     logger.info("Requisição para substituir todos os eventos recebida", quantidade=len(events_new))
#     if not events_new:
#         raise_http(logger.warning, 400, "Lista vazia enviada")

#     # Notifica via WebSocket
#     asyncio.create_task(notify_replace_started())
    
#     result = repo.replace_all(events_new)
    
#     # Notifica via WebSocket
#     asyncio.create_task(notify_replace_done())
#     asyncio.create_task(notify_user_count())
#     logger.info("Todos os eventos foram substituídos com sucesso", total=len(result))
    
#     return result

# @router.put(
#     "/{event_id}",
#     summary="Substitui os dados de um evento existente.",
#     response_model=EventResponse,
#     dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
#     responses={
#         200: {"description": "Evento substituído com sucesso."},
#         404: {"description": "Evento não encontrado."}
#     },
# )
# def put_event_by_id(
#                             event_id: int, 
#                             new_event: EventResponse,
#                             repo: AbstractEventRepo = _provide_event_repo,
#     ) -> EventResponse:
#     """
#     Substitui por completo os dados de um evento existente pelo ID.
#     """
#     logger.info("Requisição para substituir evento por ID recebida", event_id=event_id)
#     if repo.get(event_id) is None:
#         raise_http(logger.warning, 404, "Nenhum evento encontrado", event_id=event_id)

#     new_event.id = event_id  # Garante que o ID informado será usado
#     resultado = repo.replace_by_id(event_id, new_event)
#     logger.info("Evento substituído com sucesso", event_id=event_id)
#     return resultado

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

@router.delete(
    "/{event_id}",
    summary="Remove um evento específico pelo ID.",
    response_model=dict,
    # dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        200: {"description": "Evento removido com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
    # status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event(
    event_id: int,
    repo: EventRepository = _provide_event_repo, # Depends(get_event_repo),
) -> dict[str, str]:
    """
    Remove um evento pelo seu ID.
    """
    logger.info("Requisição para deletar evento recebida", event_id=event_id)
    # sucesso = repo.delete_by_id(event_id)
    # if not sucesso:
    #     raise_http(logger.warning, 404, "Evento não encontrado", event_id=event_id)
    
    existing = repo.get(event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")

    repo.delete(event_id)
    
    logger.info("Evento removido com sucesso", event_id=event_id)
    return {"mensagem": f"Evento com ID {event_id} removido com sucesso."}

@router.patch(
    "/{event_id}",
    summary="Atualiza parcialmente as informações de um evento.",
    response_model=EventView,
    # dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Evento atualizado com sucesso."},
        400: {"description": "Nenhum campo válido para atualização."},
        404: {"description": "Evento não encontrado."},
        422: {"description": "Erro de validação dos dados de entrada."}
    },
)
def patch_event(
    # background_tasks: BackgroundTasks,
    event_id: int,
    payload: EventUpdate,
    repo: EventRepository = _provide_event_repo, # Depends(get_event_repo),
) -> EventView:
    """
    Atualiza parcialmente os dados do evento informado pelo ID.
    Só os campos enviados serão alterados.
    """
    logger.info("Requisição de atualização parcial recebida", event_id=event_id)
    # if not any(value is not None for value in update.model_dump().values()):
    #     raise_http(logger.warning, 400, "Nenhum campo válido para atualização enviado", event_id=event_id)

    # try:
    #     result = repo.update(event_id, update.model_dump(exclude_unset=True))
        
    #     if update.city or update.event_date:
    #         # Adiciona task em background para buscar forecast depois
    #         background_tasks.add_task(
    #             atualizar_forecast_em_background,
    #             event_id
    #         )
            
    #     logger.info("Evento atualizado com sucesso", event_id=event_id)
    #     return result
    # except ValueError:
    #     raise_http(logger.warning, 404, "Evento não encontrado", event_id=event_id)
    # raise
    
    existing = repo.get(event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")

    # aplica patch no domínio
    if payload.title is not None:
        existing.title = payload.title
    if payload.description is not None:
        existing.description = payload.description
    if payload.event_date is not None:
        existing.event_date = payload.event_date
    if payload.city is not None:
        existing.city = payload.city
    if payload.participants is not None:
        existing.participants = payload.participants
    if payload.local_id is not None:
        existing.local_id = payload.local_id
    if payload.forecast_id is not None:
        existing.forecast_id = payload.forecast_id

    updated = repo.update(existing)

    return EventView(
        id=updated.id,  # type: ignore[arg-type]
        title=updated.title,
        description=updated.description,
        event_date=updated.event_date,
        city=updated.city,
        participants=updated.participants,
        views=updated.views,
        local_id=updated.local_id,
        forecast_id=updated.forecast_id,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )

# @router.patch(
#     "/{event_id}/local_info",
#     summary="Atualiza informações do local de um evento.",
#     response_model=EventResponse,
#     dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
#     responses={
#         200: {"description": "Informações do local atualizadas com sucesso."},
#         404: {"description": "Evento não encontrado."}
#     },
# )
# def patch_event_by_id_local_info( #async?
#     background_tasks: BackgroundTasks,
#     event_id: int,
#     update: LocalInfoUpdate | None = Body(None),
#     repo: AbstractEventRepo = _provide_event_repo,
# ) -> EventResponse:
#     """
#     Atualiza o campo local_info de um evento específico.
#     """
#     if update is None:                       # ← trata JSON null
#         raise_http(logger.warning, 422, "Erro ao receber dados do Local")
#     assert update is not None # MyPy entende que daqui pra frente update não é mais None
    
#     logger.info("Requisição para atualizar local_info recebida", event_id=event_id)
#     event = repo.get(event_id)
#     if event is None:
#         raise_http(logger.warning, 404, "Evento não encontrado", event_id=event_id)
#     assert event is not None  # MyPy entende que daqui pra frente event não é mais None
    
#     update_event(event, update, attr="local_info")
    
#     # TODO verificar se ao mudar o local info, também foi alterada a cidade
    
#     if event.city or event.event_date:
#         # Adiciona task em background para buscar forecast depois
#         background_tasks.add_task(
#             atualizar_forecast_em_background,
#             event_id
#         )
    
#     logger.info("Informações do local atualizadas com sucesso", event_id=event_id)
#     return repo.replace_by_id(event_id, event)

# @router.patch(
#     "/{event_id}/forecast_info",
#     summary="Atualiza a previsão do tempo de um evento.",
#     response_model=MessageResponse,
#     dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
#     responses={
#         200: {"description": "Previsão do tempo atualizada com sucesso."},
#         404: {"description": "Evento não encontrado."},
#         502: {"description": "Erro ao obter previsão do tempo"}
#     },
# )
# def patch_event_by_id_forecast_info(
#     background_tasks: BackgroundTasks,
#     event_id: int,
#     repo: AbstractEventRepo = _provide_event_repo,
# ) -> dict:
#     """
#     Aciona a tarefa de reprocessamento do forecast do evento.
#     """
#     logger.info("Requisição para reprocessar forecast_info recebida", event_id=event_id)
    
#     event = repo.get(event_id)
#     if event is None:
#         raise_http(logger.warning, 404, "Evento não encontrado", event_id=event_id)
#     assert event is not None  # MyPy entende que daqui pra frente não é mais None
    
#     # Adiciona task em background para buscar forecast depois
#     background_tasks.add_task(
#         atualizar_forecast_em_background,
#         event_id
#     )

#     logger.info("Tarefa de atualização de forecast agendada", event_id=event_id)
#     return {"detail": "Tarefa de atualização de forecast agendada"}