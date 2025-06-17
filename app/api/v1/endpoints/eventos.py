from fastapi import APIRouter, HTTPException, Depends, status
from fastapi import Query
from fastapi import Body
from datetime import datetime, timezone
from pydantic import ValidationError
from collections.abc import Callable
from structlog import get_logger
import inspect
# import asyncio

from app.schemas.event_create import EventCreate, EventResponse
from app.schemas.local_info import LocalInfo
from app.schemas.event_update import EventUpdate, LocalInfoUpdate, ForecastInfoUpdate
from app.schemas.weather_forecast import WeatherForecast

from app.services.auth_service import get_current_user
# from app.schemas.user import User

from app.utils.cache import cached_json

from app.services.interfaces.local_info_protocol import AbstractLocalInfoService
from app.services.interfaces.forecast_info_protocol import AbstractForecastService
from app.deps import provide_local_info_service, provide_forecast_service

from app.repositories.evento import AbstractEventRepo
from app.deps import provide_evento_repo


auth_dep = Depends(get_current_user)
_provide_local_info_service = Depends(provide_local_info_service)
_provide_forecast_service = Depends(provide_forecast_service)
_provide_event_repo = Depends(provide_evento_repo)

logger = get_logger().bind(module="eventos")

router = APIRouter()

# router = APIRouter(
#     dependencies=[auth_dep]
# )

def require_roles(*allowed: str) -> Callable:
    def verifier(user = auth_dep):
        if not set(allowed) & set(user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente"
            )
        return user
    return verifier

def _update_event(
                 event: EventResponse, 
                 update: EventUpdate | LocalInfoUpdate | ForecastInfoUpdate, 
                 attr: str | None = None
):
    """
    Atualiza parcial e de forma segura o evento ou seus campos aninhados.
    - Se attr for None, atualiza diretamente os campos do evento.
    - Se attr for 'forecast_info' ou 'local_info', faz a atualização parcial segura do objeto aninhado.
    """
    
    try:
        if attr is None:
            # Atualiza os campos do evento principal
            update_data = update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(event, field, value)
        else:
            # Atualiza um campo aninhado (ex: local_info, forecast_info)
            objeto = getattr(event, attr)
            dados_atualizados = objeto.model_dump() if objeto else {}
            update_data = update.model_dump(exclude_unset=True)
            dados_atualizados.update(update_data)
            # Descobre a classe do objeto aninhado
            field_cls = type(objeto) if objeto else None
            # Se não existir, pega o type pelo update (usando __annotations__ se quiser ser mais robusto)
            if field_cls is None and hasattr(event, '__annotations__'):
                field_cls = event.__annotations__.get(attr)
            if field_cls:
                setattr(event, attr, field_cls(**dados_atualizados))
            else:
                # fallback (não deveria acontecer em uso normal)
                setattr(event, attr, dados_atualizados)
    except ValidationError as ve:
        # Você pode fazer log, print, raise HTTPException, etc
        # Exemplo: lançar erro HTTP para o FastAPI capturar e retornar pro usuário
        raise HTTPException(status_code=422, detail=ve.errors())
    return event

@router.get(
    "/local_info",
    tags=["eventos"],
    summary="Busca informações de um local pelo nome",
    response_model=LocalInfo,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Local encontrado"},
        404: {"description": "Local não encontrado"}
    },
)
@cached_json("local-info", ttl=86400)              # ⬅⬅️ _a “mágica” está aqui_
async def obter_local_info(
    location_name: str = Query(..., description="Nome do local a ser buscado"),
    service: AbstractLocalInfoService = _provide_local_info_service
):
    """
    Retorna as informações detalhadas de um local a partir do nome.
    Cache: 24 h (86400 s)
    """
    logger.info("Consulta de local iniciada", location_name=location_name)
    
    result = await service.get_by_name(location_name)
    if inspect.iscoroutine(result):
        result = await result
        
    if not result:
        logger.warning("Local não encontrado", location_name=location_name)
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return result

@router.get(
    "/forecast_info",
    tags=["eventos"],
    summary="Busca previsão do tempo para uma cidade e data/hora (mock)",
    response_model=WeatherForecast,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Previsão recebida"},
        404: {"description": "Previsão não recebida"}
    },
)
@cached_json("forecast", ttl=1800)              # ⬅⬅️ _a “mágica” está aqui_
async def obter_forecast_info(
    city: str = Query(..., description="Nome da cidade"),
    date: datetime = Query(..., description="Data e hora de referência para a previsão"),
    service: AbstractForecastService = _provide_forecast_service,
):
    """
    Retorna a previsão do tempo simulada para a cidade e data/hora informadas.
    Cache: 30 min (1800 s)
    """
    logger.info("Consulta de clima iniciada", city=city, date=date)
    forecast_info = service.get_by_city_and_datetime(city, date)
    if not forecast_info:
        logger.warning("Previsão não encontrada", city=city, date=date)
        raise HTTPException(status_code=404, detail="Previsão não encontrada")
    return forecast_info

@router.get(
    "/eventos/todos",
    deprecated=True,                                    # Marca rota como obsoleta, sem removê-la
    include_in_schema=False,                            # Oculta rota da doc quando False
    tags=["eventos"],
    summary="Lista todos os eventos registrados.",
    response_model=list[EventResponse],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Lista de eventos retornada com sucesso."},
        404: {"description": "Nenhum evento encontrado."}
    },
)
def list_events_all(repo: AbstractEventRepo = _provide_event_repo) -> list[EventResponse]:
    """
    Retorna todos os eventos cadastrados.
    """
    logger.info("Consulta de todos eventos iniciada - Rota obsoleta")
    events = repo.list_all()
    if not events:
        logger.warning("Nenhum evento encontrado - Rota obsoleta")
        raise HTTPException(status_code=404, detail="Nenhum evento encontrado.")
    return events

@router.get(
    "/eventos",
    tags=["eventos"],
    summary="Lista eventos com filtros e paginação",
    response_model=list[EventResponse],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
)
def list_events(
    skip: int = Query(0, ge=0, description="Quantos registros pular"),
    limit: int = Query(20, le=100, description="Tamanho da página"),
    city: str | None = Query(None, description="Filtrar por cidade"),
    repo: AbstractEventRepo = _provide_event_repo,
) -> list[EventResponse]:
    """
    Retorna uma fatia paginada dos eventos; opcionalmente filtra por cidade.
    """
    logger.info("Consulta de evento iniciada", skip=skip, limit=limit, city=city)
    events = repo.list_partial(skip=skip, limit=limit, city=city)
    if not events:
        logger.warning("Nenhum evento encontrado", skip=skip, limit=limit, city=city)
        raise HTTPException(404, "Nenhum evento encontrado")
    return events

@router.get(
    "/eventos/{event_id}",
    tags=["eventos"],
    summary="Obtém um evento pelo ID.",
    response_model=EventResponse,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Evento encontrado."},
        404: {"description": "Evento não encontrado."}
    },
)
def get_event_id(
                        event_id: int, 
                        repo: AbstractEventRepo = _provide_event_repo,
    ) -> EventResponse:
    """
    Busca um evento pelo seu identificador único.
    """
    logger.info("Consulta de evento", event_id=event_id)
    event = repo.get(event_id)
    if event is None:
        logger.warning("Evento não encontrado", event_id=event_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    event.views += 1
    logger.info("Atualizado os views", event_id=event_id, views=event.views)
    repo.update(event_id, event.model_dump(exclude_unset=True))
    return EventResponse.model_validate(event)

@router.get(
    "/eventos/top/soon",
    tags=["eventos"],
    summary="N eventos com data mais próxima",
    response_model=list[EventResponse],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Lista dos eventos mais próximos."},
        404: {"description": "Sem eventos futuros encontrados"}
    },
    
)
@cached_json("top-soon", ttl=10)  # snapshot ultra-curto (10 s)
async def events_top_soon(
    limit: int = Query(10, ge=1, le=50, description="Quantos eventos retornar"),
    repo: AbstractEventRepo = _provide_event_repo,
) -> list[EventResponse]:
    """
    Ordena todos os eventos pelo `event_date` ascendente
    e devolve os *limit* mais próximos da data/hora atual.
    """
    logger.info("Consulta de eventos mais próximos iniciada", limit=limit)
    agora = datetime.now(tz=timezone.utc)

    events = repo.list_all()                     # dict[int, Evento] # Corrigir para list_partial()
    proximos = (
        sorted(
            # (ev for ev in events.values() if ev.event_date >= agora),
            [ev for ev in events if ev.event_date >= agora],
            key=lambda ev: ev.event_date,
        )[:limit]
    )
    if not proximos:
        logger.warning("Nenhum evento futuro encontrado", limit=limit)
        raise HTTPException(404, "Sem eventos futuros encontrados")
    logger.info("Consulta de eventos mais próximos concluída", quantidade=len(proximos))
    return proximos

@router.get(
    "/eventos/top/most-viewed",
    tags=["eventos"],
    summary="N eventos mais vistos",
    response_model=list[EventResponse],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Lista de eventos mais vistos."},
        404: {"description": "Nenhum evento encontrado."}
    },
)
@cached_json("top-viewed", ttl=30)  # 30 s é suficiente p/ ranking
async def events_top_viewed(
    limit: int = Query(10, ge=1, le=50),
    repo: AbstractEventRepo = Depends(provide_evento_repo),
) -> list[EventResponse]:
    """
    Retorna os *limit* eventos com maior contagem de `views`.
    Empate é resolvido pela data do evento (mais próximo primeiro).
    """
    logger.info("Consulta de eventos mais vistos iniciada", limit=limit)
    events = repo.list_all()
    most_viewed = (
        sorted(
            events,
            key=lambda ev: (-ev.views, ev.event_date)  # mais views primeiro
        )[:limit]
    )
    if not most_viewed:
        logger.warning("Nenhum evento encontrado na consulta de mais vistos", limit=limit)
        raise HTTPException(404, "Nenhum evento encontrado")
    logger.info("Consulta de eventos mais vistos concluída", quantidade=len(most_viewed))
    return most_viewed

@router.post(
    "/eventos",
    tags=["eventos"],
    summary="Cria um novo evento e tenta enriquecer com previsão do tempo.",
    response_model=EventResponse,
    status_code=201,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        201: {"description": "Evento criado com sucesso, podendo conter ou não previsão do tempo."},
        207: {"description": "Evento criado, mas sem previsão do tempo por falha ao acessar a API externa."} # 207 caso queria utilizar outro
    },
)
def create_event(
    event: EventCreate,
    service: AbstractForecastService = _provide_forecast_service,
    repo: AbstractEventRepo = _provide_event_repo,
) -> EventResponse:
    """
    Cria um evento e tenta buscar a previsão do tempo automaticamente para preenchimento do campo forecast_info.
    Se a previsão não puder ser obtida, o evento é criado normalmente, porém forecast_info fica vazio.
    """
    logger.info("Recebida requisição para criar evento", title=event.title, city=event.city)
    try:
        forecast_info = service.get_by_city_and_datetime(event.city, event.event_date)
    except Exception as e:  
        logger.error("Falha ao buscar previsão do tempo", city=event.city, event_date=str(event.event_date), error=str(e))
        forecast_info = None
    
    event_resp = repo.add(event)
    event_resp.forecast_info = forecast_info
    logger.info("Evento criado", event_id=event_resp.id, title=event.title)
    return EventResponse.model_validate(event_resp)

@router.post(
    "/eventos/lote",
    tags=["eventos"],
    summary="Adiciona uma lista de novos eventos, atribuindo novos IDs.",
    response_model=list[EventResponse],
    status_code=201,
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        201: {"description": "Eventos adicionados com sucesso."},
        400: {"description": "Lista inválida enviada."}
    },
)
def add_events_batch(
    events: list[EventCreate],
    service: AbstractForecastService = _provide_forecast_service,
    repo: AbstractEventRepo = _provide_event_repo,
) -> list[EventResponse]:
    """
    Cria múltiplos eventos de uma vez, atribuindo novos IDs para cada um.
    Retorna apenas os eventos recém adicionados.
    """
    logger.info("Requisição para adicionar eventos em lote recebida", quantidade=len(events))
    if not events:
        logger.warning("Lista vazia enviada ao adicionar eventos em lote")
        raise HTTPException(status_code=400, detail="Lista inválida enviada.")

    new_events = []
    for event in events:
        try:
            forecast_info = service.get_by_city_and_datetime(event.city, event.event_date)
        except Exception as e:  
            logger.error("Falha ao buscar previsão do tempo para evento em lote", title=event.title, city=event.city, error=str(e))
            forecast_info = None

        event_resp = repo.add(event)
        event_resp.forecast_info = forecast_info
        new_events.append(EventResponse.model_validate(event_resp))
        logger.info("Evento adicionado em lote", event_id=event_resp.id, title=event.title)

    logger.info("Eventos em lote adicionados com sucesso", total_adicionados=len(new_events))
    return new_events

@router.put(
    "/eventos",
    tags=["eventos"],
    summary="Substitui todos os eventos existentes por uma nova lista.",
    response_model=list[EventResponse],
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        200: {"description": "Todos os eventos foram substituídos."},
        400: {"description": "Lista inválida enviada."}
    },
)
def replace_all_events(
    events_new: list[EventResponse],
    repo: AbstractEventRepo = _provide_event_repo,
) -> list[EventResponse]:
    """
    Substitui completamente a lista de eventos registrados.
    """
    logger.info("Requisição para substituir todos os eventos recebida", quantidade=len(events_new))
    if not events_new:
        logger.warning("Lista vazia enviada ao substituir todos os eventos")
        raise HTTPException(status_code=400, detail="Lista inválida enviada.")

    resultado = repo.replace_all(events_new)
    logger.info("Todos os eventos foram substituídos com sucesso", total=len(resultado))
    return resultado

@router.put(
    "/eventos/{event_id}",
    tags=["eventos"],
    summary="Substitui os dados de um evento existente.",
    response_model=EventResponse,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Evento substituído com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def replace_event_id(
                            event_id: int, 
                            new_event: EventResponse,
                            repo: AbstractEventRepo = _provide_event_repo,
    ) -> EventResponse:
    """
    Substitui por completo os dados de um evento existente pelo ID.
    """
    logger.info("Requisição para substituir evento por ID recebida", event_id=event_id)
    if repo.get(event_id) is None:
        logger.warning("Tentativa de substituir evento não existente", event_id=event_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    new_event.id = event_id  # Garante que o ID informado será usado
    resultado = repo.replace_by_id(event_id, new_event)
    logger.info("Evento substituído com sucesso", event_id=event_id)
    return resultado

@router.delete(
    "/eventos",
    tags=["eventos"],
    summary="Remove todos os eventos cadastrados.",
    response_model=dict,
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        200: {"description": "Todos os eventos removidos com sucesso."},
        400: {"description": "Não foi possível remover os eventos."}
    },
)
def delete_all_events(
                                repo: AbstractEventRepo = _provide_event_repo
    ) -> dict[str, str]:
    """
    Apaga todos os eventos registrados.
    """
    logger.info("Requisição para deletar todos os eventos recebida")
    try:
        repo.delete_all()
        logger.info("Todos os eventos foram removidos com sucesso")
        return {"mensagem": "Todos os eventos foram apagados com sucesso."}
    except Exception as e:
        logger.error("Erro ao tentar remover todos os eventos", error=str(e))
        raise HTTPException(status_code=400, detail="Não foi possível remover os eventos.")

@router.delete(
    "/eventos/{event_id}",
    tags=["eventos"],
    summary="Remove um evento específico pelo ID.",
    response_model=dict,
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        200: {"description": "Evento removido com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def delete_event_id(
                            event_id: int,
                            repo: AbstractEventRepo = _provide_event_repo,
    ) -> dict[str, str]:
    """
    Remove um evento pelo seu ID.
    """
    logger.info("Requisição para deletar evento recebida", event_id=event_id)
    sucesso = repo.delete_by_id(event_id)
    if not sucesso:
        logger.warning("Tentativa de deletar evento não encontrado", event_id=event_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    logger.info("Evento removido com sucesso", event_id=event_id)
    return {"mensagem": f"Evento com ID {event_id} removido com sucesso."}

@router.patch(
    "/eventos/{event_id}",
    tags=["eventos"],
    summary="Atualiza parcialmente as informações de um evento.",
    response_model=EventResponse,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Evento atualizado com sucesso."},
        400: {"description": "Nenhum campo válido para atualização."},
        404: {"description": "Evento não encontrado."},
        422: {"description": "Erro de validação dos dados de entrada."}
    },
)
def update_event(
                    event_id: int, 
                    update: EventUpdate,
                    repo: AbstractEventRepo = _provide_event_repo,
    ) -> EventResponse:
    """
    Atualiza parcialmente os dados do evento informado pelo ID.
    Só os campos enviados serão alterados.
    """
    logger.info("Requisição de atualização parcial recebida", event_id=event_id)
    if not any(value is not None for value in update.model_dump().values()):
        logger.warning("Nenhum campo válido para atualização enviado", event_id=event_id)
        raise HTTPException(status_code=400, detail="Nenhum campo válido para atualização.")

    try:
        result = repo.update(event_id, update.model_dump(exclude_unset=True))
        logger.info("Evento atualizado com sucesso", event_id=event_id)
        return result
    except ValueError:
        logger.warning("Tentativa de atualizar evento não encontrado", event_id=event_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

@router.patch(
    "/eventos/{event_id}/local_info",
    tags=["eventos"],
    summary="Atualiza informações do local de um evento.",
    response_model=EventResponse,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Informações do local atualizadas com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def update_local_info( #async?
                            event_id: int, 
                            update: LocalInfoUpdate | None = Body(None),
                            repo: AbstractEventRepo = _provide_event_repo,
    ) -> EventResponse:
    """
    Atualiza o campo local_info de um evento específico.
    """
    if update is None:                       # ← trata JSON null
        logger.warning("Erro ao receber dados do Local")
        raise HTTPException(422, "Erro ao receber dados do Local")
    
    logger.info("Requisição para atualizar local_info recebida", event_id=event_id)
    event = repo.get(event_id)
    if event is None:
        logger.warning("Tentativa de atualizar local_info de evento não encontrado", event_id=event_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    _update_event(event, update, attr="local_info")
    logger.info("Informações do local atualizadas com sucesso", event_id=event_id)
    return repo.replace_by_id(event_id, event)

@router.patch(
    "/eventos/{event_id}/forecast_info",
    tags=["eventos"],
    summary="Atualiza a previsão do tempo de um evento.",
    response_model=EventResponse,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Previsão do tempo atualizada com sucesso."},
        404: {"description": "Evento não encontrado."},
        502: {"description": "Erro ao obter previsão do tempo"}
    },
)
def update_forecast_info(
                            event_id: int,
                            service: AbstractForecastService = _provide_forecast_service,
                            repo: AbstractEventRepo = _provide_event_repo,
) -> EventResponse:
    """
    Atualiza o campo forecast_info de um evento específico.
    """
    logger.info("Requisição para atualizar forecast_info recebida", event_id=event_id)
    event = repo.get(event_id)
    if event is None:
        logger.warning("Tentativa de atualizar forecast_info de evento não encontrado", event_id=event_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    try:
        forecast = service.get_by_city_and_datetime(event.city, event.event_date)
        if forecast is not None:
            update = ForecastInfoUpdate.model_validate(forecast.model_dump())
    except Exception as e:  
        logger.error("Erro ao obter previsão do tempo", event_id=event_id, error=str(e))
        raise HTTPException(status_code=502, detail="Erro ao obter previsão do tempo")

    _update_event(event, update, attr="forecast_info")
    logger.info("Forecast_info atualizado com sucesso", event_id=event_id)
    return repo.replace_by_id(event_id, event)