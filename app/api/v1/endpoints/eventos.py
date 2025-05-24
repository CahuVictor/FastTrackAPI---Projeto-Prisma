from fastapi import APIRouter, HTTPException, Depends
from fastapi import Query
from datetime import datetime
from pydantic import ValidationError

from app.schemas.event_create import EventCreate, EventResponse
from app.schemas.local_info import LocalInfo
from app.schemas.event_update import EventUpdate, LocalInfoUpdate, ForecastInfoUpdate
from app.schemas.weather_forecast import WeatherForecast

from app.services.auth import get_current_user
from app.schemas.user import User

from app.services.mock_local_info import get_local_info_by_name
from app.services.mock_forecast_info import get_mocked_forecast_info

router = APIRouter()

# router = APIRouter(
#     dependencies=[Depends(get_current_user)]
# )

# Armazenamento em memória
eventos_db: dict[int,EventResponse] = {}
id_counter = 1

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
    dependencies=[Depends(get_current_user)],
    responses={
        404: {"description": "Local não encontrado"}
    },
)
def obter_local_info(location_name: str = Query(..., description="Nome do local a ser buscado")):
    """
    Retorna as informações detalhadas de um local a partir do nome, buscando dados simulados.
    """
    info = get_local_info_by_name(location_name)
    if not info:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return info

@router.get(
    "/forecast_info",
    tags=["eventos"],
    summary="Busca previsão do tempo para uma cidade e data/hora (mock)",
    response_model=WeatherForecast,
    dependencies=[Depends(get_current_user)],
    responses={
        404: {"description": "Previsão não encontrada"}
    },
)
def obter_forecast_info(
    city: str = Query(..., description="Nome da cidade"),
    date: datetime = Query(..., description="Data e hora de referência para a previsão"),
):
    """
    Retorna a previsão do tempo simulada para a cidade e data/hora informadas.
    """
    previsao = get_mocked_forecast_info(city, date)  # Ajuste sua função mock para aceitar city e date!
    if not previsao:
        raise HTTPException(status_code=404, detail="Previsão não encontrada")
    return previsao

@router.get(
    "/eventos",
    tags=["eventos"],
    summary="Lista todos os eventos registrados.",
    response_model=list[EventResponse],
    dependencies=[Depends(get_current_user)],
    responses={
        200: {"description": "Lista de eventos retornada com sucesso."},
        404: {"description": "Nenhum evento encontrado."}
    },
)
def listar_eventos() -> list[EventResponse]:
    """
    Retorna todos os eventos cadastrados.
    """
    global eventos_db
    if not eventos_db:
        raise HTTPException(status_code=404, detail="Nenhum evento encontrado.")
    return list(eventos_db.values())

@router.get(
    "/eventos/{evento_id}",
    tags=["eventos"],
    summary="Obtém um evento pelo ID.",
    response_model=EventResponse,
    dependencies=[Depends(get_current_user)],
    responses={
        200: {"description": "Evento encontrado."},
        404: {"description": "Evento não encontrado."}
    },
)
def obter_evento_por_id(evento_id: int) -> EventResponse:
    """
    Busca um evento pelo seu identificador único.
    """
    global eventos_db
    evento = eventos_db.get(evento_id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return EventResponse.model_validate(evento)

@router.post(
    "/eventos",
    tags=["eventos"],
    summary="Cria um novo evento e tenta enriquecer com previsão do tempo.",
    response_model=EventResponse,
    status_code=201,
    dependencies=[Depends(get_current_user)],
    responses={
        201: {"description": "Evento criado com sucesso, podendo conter ou não previsão do tempo."},
        201: {"description": "Evento criado, mas sem previsão do tempo por falha ao acessar a API externa."} # 207 caso queria utilizar outro
    },
)
def criar_evento(evento: EventCreate) -> EventResponse:
    """
    Cria um evento e tenta buscar a previsão do tempo automaticamente para preenchimento do campo forecast_info.
    Se a previsão não puder ser obtida, o evento é criado normalmente, porém forecast_info fica vazio.
    """
    global eventos_db, id_counter
    forecast_info = None
    try:
        forecast_info = get_mocked_forecast_info(evento.city, evento.event_date)
    except Exception:
        forecast_info = None
    evento_resp = EventResponse(
        id=id_counter,
        title=evento.title,
        description=evento.description,
        event_date=evento.event_date,
        city=evento.city,
        participants=evento.participants,
        local_info=evento.local_info,
        forecast_info=forecast_info
    )
    eventos_db[id_counter] = evento_resp
    id_counter += 1
    # if forecast_info is None:
    #     return JSONResponse(
    #         status_code=201,
    #         content={**evento_resp.model_dump(), "detalhe": "Evento criado sem previsão do tempo."}
    #     )
    # else:
    #     return EventResponse.model_validate(evento_resp)
    return EventResponse.model_validate(evento_resp)

@router.post(
    "/eventos/lote",
    tags=["eventos"],
    summary="Adiciona uma lista de novos eventos, atribuindo novos IDs.",
    response_model=list[EventResponse],
    status_code=201,
    dependencies=[Depends(get_current_user)],
    responses={
        201: {"description": "Eventos adicionados com sucesso."},
        400: {"description": "Lista inválida enviada."}
    },
)
def adicionar_eventos_em_lote(eventos: list[EventCreate]) -> list[EventResponse]:
    """
    Cria múltiplos eventos de uma vez, atribuindo novos IDs para cada um.
    Retorna apenas os eventos recém adicionados.
    """
    global id_counter, eventos_db
    if not eventos:
        raise HTTPException(status_code=400, detail="Lista inválida enviada.")
    novos_eventos = []
    for evento in eventos:
        forecast_info = get_mocked_forecast_info(evento.city, evento.event_date)
        evento_resp = EventResponse(
            id=id_counter,
            title=evento.title,
            description=evento.description,
            event_date=evento.event_date,
            city=evento.city,
            participants=evento.participants,
            local_info=evento.local_info,
            forecast_info=forecast_info
        )
        eventos_db[id_counter] = evento_resp
        id_counter += 1
        novos_eventos.append(evento_resp)
    return novos_eventos

@router.put(
    "/eventos",
    tags=["eventos"],
    summary="Substitui todos os eventos existentes por uma nova lista.",
    response_model=list[EventResponse],
    dependencies=[Depends(get_current_user)],
    responses={
        200: {"description": "Todos os eventos foram substituídos."},
        400: {"description": "Lista inválida enviada."}
    },
)
def substituir_todos_os_eventos(eventos: list[EventResponse]) -> list[EventResponse]:
    """
    Substitui completamente a lista de eventos registrados.
    """
    global eventos_db
    if not eventos:
        raise HTTPException(status_code=400, detail="Lista inválida enviada.")
    eventos_db.clear()
    for evento in eventos:
        eventos_db[evento.id] = evento
    return list(eventos_db.values())

@router.put(
    "/eventos/{evento_id}",
    tags=["eventos"],
    summary="Substitui os dados de um evento existente.",
    response_model=EventResponse,
    dependencies=[Depends(get_current_user)],
    responses={
        200: {"description": "Evento substituído com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def substituir_evento_por_id(evento_id: int, novo_evento: EventResponse) -> EventResponse:
    """
    Substitui por completo os dados de um evento existente pelo ID.
    """
    global eventos_db
    if evento_id not in eventos_db:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    novo_evento.id = evento_id
    eventos_db[evento_id] = novo_evento
    return novo_evento

@router.delete(
    "/eventos",
    tags=["eventos"],
    summary="Remove todos os eventos cadastrados.",
    response_model=dict,
    dependencies=[Depends(get_current_user)],
    responses={
        200: {"description": "Todos os eventos removidos com sucesso."},
        400: {"description": "Não foi possível remover os eventos."}
    },
)
def deletar_todos_os_eventos() -> dict[str, str]:
    """
    Apaga todos os eventos registrados.
    """
    global eventos_db
    eventos_db.clear()
    return {"mensagem": "Todos os eventos foram apagados com sucesso."}

@router.delete(
    "/eventos/{evento_id}",
    tags=["eventos"],
    summary="Remove um evento específico pelo ID.",
    response_model=dict,
    dependencies=[Depends(get_current_user)],
    responses={
        200: {"description": "Evento removido com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def deletar_evento_por_id(evento_id: int) -> dict[str, str]:
    """
    Remove um evento pelo seu ID.
    """
    global eventos_db
    evento = eventos_db.pop(evento_id, None)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    return {"mensagem": f"Evento com ID {evento_id} removido com sucesso."}

@router.patch(
    "/eventos/{evento_id}",
    tags=["eventos"],
    summary="Atualiza parcialmente as informações de um evento.",
    response_model=EventResponse,
    dependencies=[Depends(get_current_user)],
    responses={
        200: {"description": "Evento atualizado com sucesso."},
        400: {"description": "Nenhum campo válido para atualização."},
        404: {"description": "Evento não encontrado."}
    },
)
def atualizar_evento(evento_id: int, atualizacao: EventUpdate) -> EventResponse:
    """
    Atualiza parcialmente os dados do evento informado pelo ID.
    Só os campos enviados serão alterados.
    """
    global eventos_db
    if evento_id not in eventos_db:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    evento = eventos_db[evento_id]
    
    if atualizacao is None:
        raise HTTPException(status_code=502, detail="Erro ao receber dados do evento")
    
    if not isinstance(atualizacao, EventUpdate):
        raise HTTPException(status_code=500, detail="Tipo inválido para EventUpdate")
    
    if not any(value is not None for value in atualizacao.model_dump().values()):
        raise HTTPException(status_code=400, detail="Nenhum campo válido para atualização.")
    
    update_event(evento, atualizacao)

    eventos_db[evento_id] = evento
    return evento

@router.patch(
    "/eventos/{evento_id}/local_info",
    tags=["eventos"],
    summary="Atualiza informações do local de um evento.",
    response_model=EventResponse,
    dependencies=[Depends(get_current_user)],
    responses={
        200: {"description": "Informações do local atualizadas com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def atualizar_local_info(evento_id: int, atualizacao: LocalInfoUpdate) -> EventResponse:
    """
    Atualiza o campo local_info de um evento específico.
    """
    global eventos_db
    if evento_id not in eventos_db:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    evento = eventos_db[evento_id]
    
    if atualizacao is None:
        raise HTTPException(status_code=502, detail="Erro ao receber dados do Local")
    
    if not isinstance(atualizacao, LocalInfoUpdate):
        raise HTTPException(status_code=500, detail="Tipo inválido para LocalInfoUpdate")
    
    update_event(evento, atualizacao, attr='local_info')

    eventos_db[evento_id] = evento

    return EventResponse.model_validate(evento)

@router.patch(
    "/eventos/{evento_id}/forecast_info",
    tags=["eventos"],
    summary="Atualiza a previsão do tempo de um evento.",
    response_model=EventResponse,
    dependencies=[Depends(get_current_user)],
    responses={
        200: {"description": "Previsão do tempo atualizada com sucesso."},
        404: {"description": "Evento não encontrado."}
    },
)
def atualizar_forecast_info(evento_id: int) -> EventResponse:
    """
    Atualiza o campo forecast_info de um evento específico.
    """
    global eventos_db
    if evento_id not in eventos_db:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    
    evento = eventos_db[evento_id]
    
    atualizacao = None
    try:
        __atualizacao = get_mocked_forecast_info(evento.city, evento.event_date)
        atualizacao = ForecastInfoUpdate.model_validate(__atualizacao.model_dump())
    except Exception:
        atualizacao = None
    
    if atualizacao is None:
        raise HTTPException(status_code=502, detail="Erro ao obter previsão do tempo")
    
    # if not isinstance(atualizacao, ForecastInfoUpdate):
    #     raise HTTPException(status_code=500, detail="Tipo inválido para forecast_info")
    
    update_event(evento, atualizacao, attr='forecast_info')

    eventos_db[evento_id] = evento
    
    return EventResponse.model_validate(evento)