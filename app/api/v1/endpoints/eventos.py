from fastapi import APIRouter, HTTPException, Depends, status
from fastapi import Query
from datetime import datetime, timezone
from pydantic import ValidationError
from collections.abc import Callable
from structlog import get_logger

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

from app.repositories.evento import AbstractEventoRepo
from app.deps import provide_evento_repo


auth_dep = Depends(get_current_user)
_provide_local_info_service = Depends(provide_local_info_service)
_provide_forecast_service = Depends(provide_forecast_service)
_provide_evento_repo = Depends(provide_evento_repo)

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

def update_event(
                 evento: EventResponse, 
                 atualizacao: EventUpdate | LocalInfoUpdate | ForecastInfoUpdate, 
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
            update_data = atualizacao.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(evento, field, value)
        else:
            # Atualiza um campo aninhado (ex: local_info, forecast_info)
            objeto = getattr(evento, attr)
            dados_atualizados = objeto.model_dump() if objeto else {}
            update_data = atualizacao.model_dump(exclude_unset=True)
            dados_atualizados.update(update_data)
            # Descobre a classe do objeto aninhado
            field_cls = type(objeto) if objeto else None
            # Se não existir, pega o type pelo update (usando __annotations__ se quiser ser mais robusto)
            if field_cls is None and hasattr(evento, '__annotations__'):
                field_cls = evento.__annotations__.get(attr)
            if field_cls:
                setattr(evento, attr, field_cls(**dados_atualizados))
            else:
                # fallback (não deveria acontecer em uso normal)
                setattr(evento, attr, dados_atualizados)
    except ValidationError as ve:
        # Você pode fazer log, print, raise HTTPException, etc
        # Exemplo: lançar erro HTTP para o FastAPI capturar e retornar pro usuário
        raise HTTPException(status_code=422, detail=ve.errors())
    return evento

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
    info = await service.get_by_name(location_name)
    if not info:
        logger.warning("Local não encontrado", location_name=location_name)
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return info

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
    previsao = service.get_by_city_and_datetime(city, date)
    if not previsao:
        logger.warning("Previsão não encontrada", city=city, date=date)
        raise HTTPException(status_code=404, detail="Previsão não encontrada")
    return previsao

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
def listar_eventos_todos(repo: AbstractEventoRepo = _provide_evento_repo) -> list[EventResponse]:
    """
    Retorna todos os eventos cadastrados.
    """
    logger.info("Consulta de todos eventos iniciada - Rota obsoleta")
    eventos = repo.list_all()
    if not eventos:
        logger.warning("Nenhum evento encontrado - Rota obsoleta")
        raise HTTPException(status_code=404, detail="Nenhum evento encontrado.")
    return eventos

@router.get(
    "/eventos",
    tags=["eventos"],
    summary="Lista eventos com filtros e paginação",
    response_model=list[EventResponse],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
)
def listar_eventos(
    skip: int = Query(0, ge=0, description="Quantos registros pular"),
    limit: int = Query(20, le=100, description="Tamanho da página"),
    city: str | None = Query(None, description="Filtrar por cidade"),
    repo: AbstractEventoRepo = _provide_evento_repo,
) -> list[EventResponse]:
    """
    Retorna uma fatia paginada dos eventos; opcionalmente filtra por cidade.
    """
    logger.info("Consulta de evento iniciada", skip=skip, limit=limit, city=city)
    eventos = repo.list_partial(skip=skip, limit=limit, city=city)
    if not eventos:
        logger.warning("Nenhum evento encontrado", skip=skip, limit=limit, city=city)
        raise HTTPException(404, "Nenhum evento encontrado")
    return eventos

@router.get(
    "/eventos/{evento_id}",
    tags=["eventos"],
    summary="Obtém um evento pelo ID.",
    response_model=EventResponse,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Evento encontrado."},
        404: {"description": "Evento não encontrado."}
    },
)
def obter_evento_por_id(
                        evento_id: int, 
                        repo: AbstractEventoRepo = _provide_evento_repo,
    ) -> EventResponse:
    """
    Busca um evento pelo seu identificador único.
    """
    logger.info("Consulta de evento", evento_id=evento_id)
    evento = repo.get(evento_id)
    if evento is None:
        logger.warning("Evento não encontrado", evento_id=evento_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    evento.views += 1
    logger.info("Atualizado os views", evento_id=evento_id, views=evento.views)
    repo.update(evento_id, evento.model_dump(exclude_unset=True))
    return EventResponse.model_validate(evento)

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
async def eventos_proximos(
    limit: int = Query(10, ge=1, le=50, description="Quantos eventos retornar"),
    repo: AbstractEventoRepo = _provide_evento_repo,
) -> list[EventResponse]:
    """
    Ordena todos os eventos pelo `event_date` ascendente
    e devolve os *limit* mais próximos da data/hora atual.
    """
    logger.info("Consulta de eventos mais próximos iniciada", limit=limit)
    agora = datetime.now(tz=timezone.utc)

    eventos = repo.list_all()                     # dict[int, Evento] # Corrigir para list_partial()
    proximos = (
        sorted(
            # (ev for ev in eventos.values() if ev.event_date >= agora),
            [ev for ev in eventos if ev.event_date >= agora],
            key=lambda ev: ev.event_date,
        )[:limit]
    )
    if not proximos:
        logger.warning("Nenhum evento futuro encontrado", limit=limit)
        raise HTTPException(404, "Sem eventos futuros encontrados")
    logger.info("Consulta de eventos mais próximos concluída", quantidade=len(proximos))
    return proximos

@router.get(
    "eventos/top/most-viewed",
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
async def eventos_mais_vistos(
    limit: int = Query(10, ge=1, le=50),
    repo: AbstractEventoRepo = Depends(provide_evento_repo),
) -> list[EventResponse]:
    """
    Retorna os *limit* eventos com maior contagem de `views`.
    Empate é resolvido pela data do evento (mais próximo primeiro).
    """
    logger.info("Consulta de eventos mais vistos iniciada", limit=limit)
    eventos = repo.list_all()
    mais_vistos = (
        sorted(
            eventos,
            key=lambda ev: (-ev.views, ev.event_date)  # mais views primeiro
        )[:limit]
    )
    if not mais_vistos:
        logger.warning("Nenhum evento encontrado na consulta de mais vistos", limit=limit)
        raise HTTPException(404, "Nenhum evento encontrado")
    logger.info("Consulta de eventos mais vistos concluída", quantidade=len(mais_vistos))
    return mais_vistos

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
def criar_evento(
    evento: EventCreate,
    service: AbstractForecastService = _provide_forecast_service,
    repo: AbstractEventoRepo = _provide_evento_repo,
) -> EventResponse:
    """
    Cria um evento e tenta buscar a previsão do tempo automaticamente para preenchimento do campo forecast_info.
    Se a previsão não puder ser obtida, o evento é criado normalmente, porém forecast_info fica vazio.
    """
    logger.info("Recebida requisição para criar evento", title=evento.title, city=evento.city)
    try:
        forecast_info = service.get_by_city_and_datetime(evento.city, evento.event_date)
    except Exception:
        logger.error("Falha ao buscar previsão do tempo", city=evento.city, event_date=str(evento.event_date), error=str(e))
        forecast_info = None
    
    evento_resp = repo.add(evento)
    evento_resp.forecast_info = forecast_info
    logger.info("Evento criado", event_id=evento_resp.id, title=evento.title)
    return EventResponse.model_validate(evento_resp)

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
def adicionar_eventos_em_lote(
    eventos: list[EventCreate],
    service: AbstractForecastService = _provide_forecast_service,
    repo: AbstractEventoRepo = _provide_evento_repo,
) -> list[EventResponse]:
    """
    Cria múltiplos eventos de uma vez, atribuindo novos IDs para cada um.
    Retorna apenas os eventos recém adicionados.
    """
    logger.info("Requisição para adicionar eventos em lote recebida", quantidade=len(eventos))
    if not eventos:
        logger.warning("Lista vazia enviada ao adicionar eventos em lote")
        raise HTTPException(status_code=400, detail="Lista inválida enviada.")

    novos_eventos = []
    for evento in eventos:
        try:
            forecast_info = service.get_by_city_and_datetime(evento.city, evento.event_date)
        except Exception:
            logger.error("Falha ao buscar previsão do tempo para evento em lote", title=evento.title, city=evento.city, error=str(e))
            forecast_info = None

        evento_resp = repo.add(evento)
        evento_resp.forecast_info = forecast_info
        novos_eventos.append(EventResponse.model_validate(evento_resp))
        logger.info("Evento adicionado em lote", event_id=evento_resp.id, title=evento.title)

    logger.info("Eventos em lote adicionados com sucesso", total_adicionados=len(novos_eventos))
    return novos_eventos

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
def substituir_todos_os_eventos(
    eventos_new: list[EventResponse],
    repo: AbstractEventoRepo = _provide_evento_repo,
) -> list[EventResponse]:
    """
    Substitui completamente a lista de eventos registrados.
    """
    logger.info("Requisição para substituir todos os eventos recebida", quantidade=len(eventos_new))
    if not eventos_new:
        logger.warning("Lista vazia enviada ao substituir todos os eventos")
        raise HTTPException(status_code=400, detail="Lista inválida enviada.")

    resultado = repo.replace_all(eventos_new)
    logger.info("Todos os eventos foram substituídos com sucesso", total=len(resultado))
    return resultado

@router.put(
    "/eventos/{evento_id}",
    tags=["eventos"],
    summary="Substitui os dados de um evento existente.",
    response_model=EventResponse,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Evento substituído com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def substituir_evento_por_id(
                            evento_id: int, 
                            novo_evento: EventResponse,
                            repo: AbstractEventoRepo = _provide_evento_repo,
    ) -> EventResponse:
    """
    Substitui por completo os dados de um evento existente pelo ID.
    """
    logger.info("Requisição para substituir evento por ID recebida", evento_id=evento_id)
    if repo.get(evento_id) is None:
        logger.warning("Tentativa de substituir evento não existente", evento_id=evento_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    novo_evento.id = evento_id  # Garante que o ID informado será usado
    resultado = repo.replace_by_id(evento_id, novo_evento)
    logger.info("Evento substituído com sucesso", evento_id=evento_id)
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
def deletar_todos_os_eventos(
                                repo: AbstractEventoRepo = _provide_evento_repo
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
    "/eventos/{evento_id}",
    tags=["eventos"],
    summary="Remove um evento específico pelo ID.",
    response_model=dict,
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        200: {"description": "Evento removido com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def deletar_evento_por_id(
                            evento_id: int,
                            repo: AbstractEventoRepo = _provide_evento_repo,
    ) -> dict[str, str]:
    """
    Remove um evento pelo seu ID.
    """
    logger.info("Requisição para deletar evento recebida", evento_id=evento_id)
    sucesso = repo.delete_by_id(evento_id)
    if not sucesso:
        logger.warning("Tentativa de deletar evento não encontrado", evento_id=evento_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    logger.info("Evento removido com sucesso", evento_id=evento_id)
    return {"mensagem": f"Evento com ID {evento_id} removido com sucesso."}

@router.patch(
    "/eventos/{evento_id}",
    tags=["eventos"],
    summary="Atualiza parcialmente as informações de um evento.",
    response_model=EventResponse,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Evento atualizado com sucesso."},
        400: {"description": "Nenhum campo válido para atualização."},
        404: {"description": "Evento não encontrado."}
    },
)
def atualizar_evento(
                    evento_id: int, 
                    atualizacao: EventUpdate,
                    repo: AbstractEventoRepo = _provide_evento_repo,
    ) -> EventResponse:
    """
    Atualiza parcialmente os dados do evento informado pelo ID.
    Só os campos enviados serão alterados.
    """
    logger.info("Requisição de atualização parcial recebida", evento_id=evento_id)
    if not any(value is not None for value in atualizacao.model_dump().values()):
        logger.warning("Nenhum campo válido para atualização enviado", evento_id=evento_id)
        raise HTTPException(status_code=400, detail="Nenhum campo válido para atualização.")

    try:
        result = repo.update(evento_id, atualizacao.model_dump(exclude_unset=True))
        logger.info("Evento atualizado com sucesso", evento_id=evento_id)
        return result
    except ValueError:
        logger.warning("Tentativa de atualizar evento não encontrado", evento_id=evento_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

@router.patch(
    "/eventos/{evento_id}/local_info",
    tags=["eventos"],
    summary="Atualiza informações do local de um evento.",
    response_model=EventResponse,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Informações do local atualizadas com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def atualizar_local_info(
                            evento_id: int, 
                            atualizacao: LocalInfoUpdate,
                            repo: AbstractEventoRepo = _provide_evento_repo,
    ) -> EventResponse:
    """
    Atualiza o campo local_info de um evento específico.
    """
    logger.info("Requisição para atualizar local_info recebida", evento_id=evento_id)
    evento = repo.get(evento_id)
    if evento is None:
        logger.warning("Tentativa de atualizar local_info de evento não encontrado", evento_id=evento_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    update_event(evento, atualizacao, attr="local_info")
    logger.info("Informações do local atualizadas com sucesso", evento_id=evento_id)
    return repo.replace_by_id(evento_id, evento)

@router.patch(
    "/eventos/{evento_id}/forecast_info",
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
def atualizar_forecast_info(
                            evento_id: int,
                            service: AbstractForecastService = _provide_forecast_service,
                            repo: AbstractEventoRepo = _provide_evento_repo,
) -> EventResponse:
    """
    Atualiza o campo forecast_info de um evento específico.
    """
    logger.info("Requisição para atualizar forecast_info recebida", evento_id=evento_id)
    evento = repo.get(evento_id)
    if evento is None:
        logger.warning("Tentativa de atualizar forecast_info de evento não encontrado", evento_id=evento_id)
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    try:
        forecast = service.get_by_city_and_datetime(evento.city, evento.event_date)
        if forecast is not None:
            atualizacao = ForecastInfoUpdate.model_validate(forecast.model_dump())
    except Exception:
        logger.error("Erro ao obter previsão do tempo", evento_id=evento_id, error=str(e))
        raise HTTPException(status_code=502, detail="Erro ao obter previsão do tempo")

    update_event(evento, atualizacao, attr="forecast_info")
    logger.info("Forecast_info atualizado com sucesso", evento_id=evento_id)
    return repo.replace_by_id(evento_id, evento)