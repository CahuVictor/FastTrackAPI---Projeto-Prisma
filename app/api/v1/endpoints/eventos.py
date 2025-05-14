from fastapi import APIRouter, HTTPException
from app.schemas.event_create import EventCreate, EventResponse
from app.schemas.local_info import LocalInfo
from app.schemas.event_update import EventUpdate

router = APIRouter()

# Armazenamento em memória
eventos_db: dict[int,EventResponse] = {}
id_counter = 1

def buscar_local_info(location_name: str) -> LocalInfo:
    if location_name.lower() == "CESAR":
        return LocalInfo(
            location_name=location_name,
            capacity=200,
            venue_type="Auditorio",
            is_accessible=True,
            address="Rua Bione, 220",
            past_events=["Recn'n Play 2018", "Recn'n Play 2019", "Recn'n Play 2023", "Recn'n Play 2024"]
        )
    return LocalInfo(location_name=location_name, capacity=2, venue_type="Auditorio", is_accessible=False, address="Rua Exemplo, 123", past_events=[])

@router.get("/eventos", tags=["eventos"])
def listar_eventos()->list[EventResponse]:
    global eventos_db
    return list(eventos_db.values())

@router.get("/eventos/{evento_id}", tags=["eventos"])
def obter_evento_por_id(evento_id: int)->EventResponse:
    global eventos_db
    evento = eventos_db.get(evento_id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return EventResponse.model_validate(evento)

@router.post("/eventos", tags=["eventos"])
def criar_evento(evento: EventCreate)->EventResponse:
# def criar_evento(title: str, description: str, event_date: str, participants: list[str], location_name: str):
    global eventos_db, id_counter
    # evento.id = id_counter
    # local_info = buscar_local_info(location_name)  # ❌ erro aqui
    location_name = evento.local_info.location_name  # ✅ Pega o valor corretamente
    local_info = buscar_local_info(location_name)
    evento = EventResponse(
        id=id_counter,
        title=evento.title,
        description=evento.description,
        event_date=evento.event_date,
        participants=evento.participants,
        local_info=local_info
        # adicionar forecat
    )
    eventos_db[id_counter] = evento
    id_counter += 1
    return EventResponse.model_validate(evento)

@router.put("/eventos", tags=["eventos"])
# def substituir_todos_os_eventos(eventos: list[EventCreate])->list[EventCreate]:
def substituir_todos_os_eventos(eventos: list[EventResponse])->list[EventResponse]:
    global eventos_db, id_counter
    eventos_db = {}
    # id_counter = 1 Assume que o novo objeto já vem com o id
    for evento in eventos:
        # evento.id = id_counter
        # eventos_db[id_counter] = evento
        # id_counter += 1
        eventos_db[evento.id] = evento
    return list(eventos_db.values())

@router.put("/eventos/{evento_id}", tags=["eventos"])
def substituir_evento_por_id(evento_id: int, novo_evento: EventResponse)->EventResponse:
    global eventos_db
    if evento_id not in eventos_db:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    novo_evento.id = evento_id
    eventos_db[evento_id] = novo_evento
    return novo_evento

@router.delete("/eventos", tags=["eventos"])
def deletar_todos_os_eventos()->dict[str,str]:
    global eventos_db
    eventos_db = {}
    return {"mensagem": "Todos os eventos foram apagados com sucesso"}

@router.delete("/eventos/{evento_id}", tags=["eventos"])
# def deletar_evento_por_id(evento_id: int)->EventCreate:
def deletar_evento_por_id(evento_id: int)->dict[str,str]:
    global eventos_db
    # if evento_id not in eventos_db:
    #     raise HTTPException(status_code=404, detail="Evento não encontrado")
    # del_evento = eventos_db[evento_id]
    # del eventos_db[evento_id]
    # return del_evento
    evento = eventos_db.pop(evento_id, None)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return {"mensagem": f"Evento com ID {evento_id} removido com sucesso"}

@router.patch("/eventos", tags=["eventos"])
def concatenar_eventos(eventos: list[EventResponse])->list[EventResponse]:
    global id_counter, eventos_db
    novos_eventos = []
    for evento in eventos:
        evento.id = id_counter
        eventos_db[id_counter] = evento
        id_counter += 1
        novos_eventos.append(evento)
    return novos_eventos

@router.patch("/eventos/{evento_id}", tags=["eventos"])
def atualizar_parcial_evento(evento_id: int, atualizacao: EventUpdate)->EventResponse:
    global eventos_db
    if evento_id not in eventos_db:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    evento = eventos_db[evento_id]
    if atualizacao.local_info:
        evento.local_info = atualizacao.local_info
    if atualizacao.forecast_info:
        evento.forecast_info = atualizacao.forecast_info
    return EventResponse.model_validate(evento)
