from fastapi import APIRouter, HTTPException, Depends, status
from fastapi import Query
from datetime import datetime
from pydantic import ValidationError
from typing import Callable

from app.schemas.event_create import EventCreate, EventResponse
from app.schemas.local_info import LocalInfo
from app.schemas.event_update import EventUpdate, LocalInfoUpdate, ForecastInfoUpdate
from app.schemas.weather_forecast import WeatherForecast

from app.services.auth_service import get_current_user
# from app.schemas.user import User

from app.services.interfaces.local_info import AbstractLocalInfoService
from app.services.interfaces.forecast_info import AbstractForecastService
from app.deps import provide_local_info_service, provide_forecast_service

from app.repositories.evento import AbstractEventoRepo
from app.deps import provide_evento_repo


auth_dep = Depends(get_current_user)
_provide_local_info_service = Depends(provide_local_info_service)
_provide_forecast_service = Depends(provide_forecast_service)

router = APIRouter()

# router = APIRouter(
#     dependencies=[auth_dep]
# )

# Armazenamento em memória
id_counter = 1

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
    summary="Busca informações de um local (mock)",
    response_model=LocalInfo,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        404: {"description": "Local não encontrado"}
    },
)
def obter_local_info(
    location_name: str = Query(..., description="Nome do local a ser buscado"),
    service: AbstractLocalInfoService = _provide_local_info_service
):
    """
    Retorna as informações detalhadas de um local a partir do nome, buscando dados simulados.
    """
    info = service.get_by_name(location_name)
    if not info:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return info

@router.get(
    "/forecast_info",
    tags=["eventos"],
    summary="Busca previsão do tempo para uma cidade e data/hora (mock)",
    response_model=WeatherForecast,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        404: {"description": "Previsão não encontrada"}
    },
)
def obter_forecast_info(
    city: str = Query(..., description="Nome da cidade"),
    date: datetime = Query(..., description="Data e hora de referência para a previsão"),
    service: AbstractForecastService = _provide_forecast_service,
):
    """
    Retorna a previsão do tempo simulada para a cidade e data/hora informadas.
    """
    previsao = service.get_by_city_and_datetime(city, date)
    if not previsao:
        raise HTTPException(status_code=404, detail="Previsão não encontrada")
    return previsao

@router.get(
    "/eventos",
    tags=["eventos"],
    summary="Lista todos os eventos registrados.",
    response_model=list[EventResponse],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor", "viewer"))],
    responses={
        200: {"description": "Lista de eventos retornada com sucesso."},
        404: {"description": "Nenhum evento encontrado."}
    },
)
def listar_eventos(repo: AbstractEventoRepo = Depends(provide_evento_repo)) -> list[EventResponse]:
    """
    Retorna todos os eventos cadastrados.
    """
    eventos = repo.list_all()
    if not eventos:
        raise HTTPException(status_code=404, detail="Nenhum evento encontrado.")
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
                        repo: AbstractEventoRepo = Depends(provide_evento_repo),
    ) -> EventResponse:
    """
    Busca um evento pelo seu identificador único.
    """
    evento = repo.get(evento_id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return EventResponse.model_validate(evento)

@router.post(
    "/eventos",
    tags=["eventos"],
    summary="Cria um novo evento e tenta enriquecer com previsão do tempo.",
    response_model=EventResponse,
    status_code=201,
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        201: {"description": "Evento criado com sucesso, podendo conter ou não previsão do tempo."},
        201: {"description": "Evento criado, mas sem previsão do tempo por falha ao acessar a API externa."} # 207 caso queria utilizar outro
    },
)
def criar_evento(
    evento: EventCreate,
    service: AbstractForecastService = _provide_forecast_service,
    repo: AbstractEventoRepo = Depends(provide_evento_repo),
) -> EventResponse:
    """
    Cria um evento e tenta buscar a previsão do tempo automaticamente para preenchimento do campo forecast_info.
    Se a previsão não puder ser obtida, o evento é criado normalmente, porém forecast_info fica vazio.
    """
    try:
        forecast_info = service.get_by_city_and_datetime(evento.city, evento.event_date)
    except Exception:
        forecast_info = None
    
    evento_resp = repo.add(evento)
    evento_resp.forecast_info = forecast_info
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
    service: AbstractForecastService = Depends(provide_forecast_service),
    repo: AbstractEventoRepo = Depends(provide_evento_repo),
) -> list[EventResponse]:
    """
    Cria múltiplos eventos de uma vez, atribuindo novos IDs para cada um.
    Retorna apenas os eventos recém adicionados.
    """
    if not eventos:
        raise HTTPException(status_code=400, detail="Lista inválida enviada.")

    novos_eventos = []
    for evento in eventos:
        try:
            forecast_info = service.get_by_city_and_datetime(evento.city, evento.event_date)
        except Exception:
            forecast_info = None

        evento_resp = repo.add(evento)
        evento_resp.forecast_info = forecast_info
        novos_eventos.append(EventResponse.model_validate(evento_resp))

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
    repo: AbstractEventoRepo = Depends(provide_evento_repo),
) -> list[EventResponse]:
    """
    Substitui completamente a lista de eventos registrados.
    """
    if not eventos_new:
        raise HTTPException(status_code=400, detail="Lista inválida enviada.")

    return repo.replace_all(eventos_new)

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
                            repo: AbstractEventoRepo = Depends(provide_evento_repo),
    ) -> EventResponse:
    """
    Substitui por completo os dados de um evento existente pelo ID.
    """
    if repo.get(evento_id) is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    novo_evento.id = evento_id  # Garante que o ID informado será usado
    return repo.replace_by_id(evento_id, novo_evento)

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
                                repo: AbstractEventoRepo = Depends(provide_evento_repo)
    ) -> dict[str, str]:
    """
    Apaga todos os eventos registrados.
    """
    repo.delete_all()
    return {"mensagem": "Todos os eventos foram apagados com sucesso."}

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
                            repo: AbstractEventoRepo = Depends(provide_evento_repo),
    ) -> dict[str, str]:
    """
    Remove um evento pelo seu ID.
    """
    sucesso = repo.delete_by_id(evento_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
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
                    repo: AbstractEventoRepo = Depends(provide_evento_repo),
    ) -> EventResponse:
    """
    Atualiza parcialmente os dados do evento informado pelo ID.
    Só os campos enviados serão alterados.
    """
    if not any(value is not None for value in atualizacao.model_dump().values()):
        raise HTTPException(status_code=400, detail="Nenhum campo válido para atualização.")

    try:
        return repo.update(evento_id, atualizacao.model_dump(exclude_unset=True))
    except ValueError:
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
                            repo: AbstractEventoRepo = Depends(provide_evento_repo),
    ) -> EventResponse:
    """
    Atualiza o campo local_info de um evento específico.
    """
    evento = repo.get(evento_id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    update_event(evento, atualizacao, attr="local_info")
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
                            repo: AbstractEventoRepo = Depends(provide_evento_repo),
) -> EventResponse:
    """
    Atualiza o campo forecast_info de um evento específico.
    """
    evento = repo.get(evento_id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    try:
        previsao = service.get_by_city_and_datetime(evento.city, evento.event_date)
        atualizacao = ForecastInfoUpdate.model_validate(previsao.model_dump())
    except Exception:
        raise HTTPException(status_code=502, detail="Erro ao obter previsão do tempo")

    update_event(evento, atualizacao, attr="forecast_info")
    return repo.replace_by_id(evento_id, evento)