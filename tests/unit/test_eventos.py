# tests/unit/test_eventos.py
# (eventos & manipulação geral)

from typing import Literal
from fastapi.testclient import TestClient
import pytest
from datetime import datetime, timedelta, timezone
# from starlette.testclient import TestClient
from io import BytesIO

# from fastapi import HTTPException

from app.main import app

from app.schemas.event_create import EventCreate

from app.deps import provide_event_repo
# from app.api.v1.endpoints.eventos import atualizar_evento
from app.repositories.event_mem import InMemoryEventRepo

# --------------------------------------------------------------------------- #
# 1. GET /eventos/{id}
# --------------------------------------------------------------------------- #
def _new_event_json(titulo="Show", dias=1, views: int = 0):
    """Helper p/ montar o payload JSON de um evento futuro/presente."""
    
    return {
        "title": titulo,
        "description": "...",
        "city": "Recife",
        "event_date": datetime.now(tz=timezone.utc).isoformat(),  # ← string
        "participants": [],
        # se tiver local_info coloque aqui…
    }

@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_create_event_valid(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido']):
    resp = client.post("/api/v1/eventos", json=event, headers=auth_header) # evento_valido
    assert resp.status_code == 201
    assert resp.json()["title"].lower() == event["title"].lower() # evento_valido

@pytest.mark.parametrize("event", ["evento_invalido"], indirect=True)
def test_create_event_invalid(client: TestClient, auth_header: dict[str, str], event: Literal['evento_invalido']):
    resp = client.post("/api/v1/eventos", json=event, headers=auth_header) # evento_invalido
    assert resp.status_code == 422

@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_get_event_by_id_ok(
    client: TestClient, auth_header: dict[str, str], event
):
    resp = client.post("/api/v1/eventos", json=event, headers=auth_header)
    ev_id = resp.json()["id"]

    resp_get = client.get(f"/api/v1/eventos/{ev_id}", headers=auth_header)

    assert resp_get.status_code == 200
    body = resp_get.json()
    assert body["id"] == ev_id
    assert body["views"] == 1  # contador é incrementado

def test_get_event_by_id_404(client: TestClient, auth_header: dict[str, str]):
    resp_get = client.get("/api/v1/eventos/9999", headers=auth_header)
    assert resp_get.status_code == 404
    assert resp_get.json()["detail"] == "Evento não encontrado"

def test_list_event(client: TestClient, auth_header: dict[str, str]):
    resp = client.get("/api/v1/eventos", headers=auth_header)
    # Pode ser 200 ou 404, dependendo se já apagou ou não
    assert resp.status_code in (200, 404)

# --------------------------------------------------------------------------- #
# 2. list_events_all – rota obsoleta que lista tudo                        #
# --------------------------------------------------------------------------- #
def test_list_events_all_ok(client: TestClient, auth_header: dict[str, str], repo):
    # cria 2 eventos
    for i in range(2):
        repo.add(EventCreate(...))  # fixture usa defaults

    resp = client.get("/api/v1/eventos/todos", headers=auth_header)  # rota legacy
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_events_all_clear(client: TestClient, auth_header: dict[str, str]):
    resp = client.get("/api/v1/eventos/todos", headers=auth_header)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Nenhum evento encontrado"

# --------------------------------------------------------------------------- #
# 3. /eventos/top/soon – sem futuros                                     #
# --------------------------------------------------------------------------- #
def test_get_top_upcoming_events_without_future(client: TestClient, auth_header: dict[str, str], repo):
    # somente eventos PASSADOS
    ontem = datetime.now(tz=timezone.utc) - timedelta(days=1)
    repo.add(
        EventCreate(
            title="passado",
            description="pass",
            city="Recife",
            event_date=ontem,
            participants=[],
        )
    )

    resp = client.get("/api/v1/eventos/top/soon", headers=auth_header)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Nenhum evento futuro encontrado"

# --------------------------------------------------------------------------- #
# 4. /eventos/top/most-viewed – sem registros                           #
# --------------------------------------------------------------------------- #
def test_top_most_viewed_clear(client: TestClient, auth_header: dict[str, str]):
    resp = client.get("/api/v1/eventos/top/most-viewed", headers=auth_header)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Nenhum evento encontrado"

@pytest.mark.parametrize("event", ["evento_valido_com_id"], indirect=True)
def test_replace_all_events(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido_com_id']):
    event["title"] = "Evento Substituto"
    resp = client.put("/api/v1/eventos", json=[event], headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()[0]["title"] == "Evento Substituto"

# Testar PUT /eventos/{id} para substituir um evento inexistente
@pytest.mark.parametrize("event", ["evento_valido_com_id_e_forecast"], indirect=True)
def test_replace_nonexistent_event(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido_com_id_e_forecast']):
    resp = client.put("/api/v1/eventos/99999", json=event, headers=auth_header)
    assert resp.status_code == 404

@pytest.mark.parametrize("event", ["evento_valido_com_id"], indirect=True)
def test_update_event_none_unit(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido_com_id']):
    """
    Testa a branch onde 'atualizacao' é None na função atualizar_evento.
    FastAPI nunca permite isso via HTTP, mas pode ocorrer em uso direto da função.
    Espera-se um HTTPException 502.
    """
    # primeiro garante que o evento existe no repositório
    client.put("/api/v1/eventos", json=[event], headers=auth_header)
    
    event_id = event["id"]
    
    resp = client.patch(
        f"/api/v1/eventos/{event_id}",
        data="null",
        headers={**auth_header, "Content-Type": "application/json"},
    )
    
    assert resp.status_code == 422          # validação falhou
    # body = resp.json()
    # (opcional) checagem da mensagem de erro de validação
    detail = resp.json()["detail"][0]
    # opcional: conferir mensagem de erro padrão do FastAPI/Pydantic
    # assert body["detail"][0]["type"] == "null_is_not_allowed"
    assert detail["type"] in {"missing", "model_attributes_type"}

@pytest.mark.parametrize("event", ["evento_valido_com_id"], indirect=True)
def test_update_event_type_invalid_unit(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido_com_id']):
    """
    Testa a branch onde 'atualizacao' é de tipo inválido na função atualizar_evento.
    FastAPI/Pydantic nunca permite isso via HTTP, mas pode ocorrer em uso direto da função.
    Espera-se um HTTPException 500.
    """
    # garante que o evento existe
    client.put("/api/v1/eventos", json=[event], headers=auth_header)
    
    event_id = event["id"]
    
    resp = client.patch(
        f"/api/v1/eventos/{event_id}",
        json=789,                       # corpo inválido
        headers=auth_header
    )

    assert resp.status_code == 422
    # (opcional) checagem da mensagem de erro de validação
    detail = resp.json()["detail"][0]
    # assert detail["type"] == "int_parsing" or detail["msg"].startswith("value is not a valid dict")
    assert detail["type"] in {"missing", "model_attributes_type"}
    
@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_replace_event_by_id(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido']):
    # 1) cria o evento original
    post = client.post("/api/v1/eventos", json=event, headers=auth_header)
    event_id = post.json()["id"]

    # 2) monta a versão completa que irá substituir
    new_event = event.copy()
    new_event["id"] = event_id          # obrigatório no PUT
    new_event["title"] = "Novo Título"

    # 3) faz a substituição
    resp = client.put(
        f"/api/v1/eventos/{event_id}",
        json=new_event,
        headers=auth_header,
    )

    assert resp.status_code == 200
    assert resp.json()["title"] == "Novo Título"

# --------------------------------------------------------------------------- #
# 5. POST /eventos/lote                                                    #
# --------------------------------------------------------------------------- #
def test_add_events_batch_ok(client: TestClient, auth_header: dict[str, str]):
    lote = [
        _new_event_json("A"),
        _new_event_json("B"),
    ]
    resp = client.post("/api/v1/eventos/lote", json=lote, headers=auth_header)

    assert resp.status_code == 201
    body = resp.json()
    assert len(body) == 2
    assert {ev["title"] for ev in body} == {"A", "B"}


def test_add_events_batch_lista_vazia(client: TestClient, auth_header: dict[str, str]):
    resp = client.post("/api/v1/eventos/lote", json=[], headers=auth_header)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Lista vazia enviada"

# --------------------------------------------------------------------------- #
# 6. DELETE /eventos/{id}                                                  #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_delete_event_ok(client: TestClient, auth_header: dict[str, str], event):
    post = client.post("/api/v1/eventos", json=event, headers=auth_header)
    ev_id = post.json()["id"]

    del_resp = client.delete(f"/api/v1/eventos/{ev_id}", headers=auth_header)
    assert del_resp.status_code == 200
    assert f"ID {ev_id}" in del_resp.json()["mensagem"]

    # confirmar que realmente não existe mais
    follow = client.get(f"/api/v1/eventos/{ev_id}", headers=auth_header)
    assert follow.status_code == 404


def test_delete_event_not_found(client: TestClient, auth_header: dict[str, str]):
    resp = client.delete("/api/v1/eventos/8888", headers=auth_header)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Evento não encontrado"

@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_delete_all_events(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido']):
    client.post("/api/v1/eventos", json=event, headers=auth_header)
    resp = client.delete("/api/v1/eventos", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["mensagem"].startswith("Todos os eventos foram apagados")

# Testar PATCH /eventos/{id} para atualizar um evento inexistente
def test_update_nonexistent_event(client: TestClient, auth_header: dict[str, str]):
    update = {"title": "Novo Título"}
    response = client.patch("/api/v1/eventos/99999", json=update, headers=auth_header)
    assert response.status_code == 404

# Testar PUT /eventos com lista vazia
def test_replace_all_events_clear(client: TestClient, auth_header: dict[str, str]):
    response = client.put("/api/v1/eventos", json=[], headers=auth_header)
    assert response.status_code == 400

# Testar erro de validação em update_event (try/except do update_event)
@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_update_event_validationerror(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido']):
    # from app.api.v1.endpoints import eventos as eventos_module
    # from pydantic import ValidationError

    # Cria evento
    post_resp = client.post("/api/v1/eventos", json=event, headers=auth_header)
    event_id = post_resp.json()["id"]

    # Envie update inválido para local_info (ex: capacity string)
    update = {"capacity": "invalido", "manually_edited": True}
    resp = client.patch(f"/api/v1/eventos/{event_id}/local_info", json=update, headers=auth_header)
    assert resp.status_code == 422
    # Detalhe do erro pode ser validado aqui se quiser

# # Testar o caso: atualizacao é None (502)
# @pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
# def test_atualizar_evento_none(client_autenticado, event):
#     # Crie um evento antes
#     post_response = client_autenticado.post("/api/v1/eventos", json=event)
#     event_id = post_response.json()["id"]
#     # Envie um body explícito None (JSON 'null')
#     response = client_autenticado.patch(f"/api/v1/eventos/{event_id}", data="null", headers={"Content-Type": "application/json"})
#     assert response.status_code == 502
#     assert response.json()["detail"] == "Erro ao receber dados do evento"

# Testar o caso: atualizacao não é EventUpdate (500)
@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_update_event_type_invalid(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido']):
    # Crie um evento antes
    post_resp = client.post("/api/v1/eventos", json=event, headers=auth_header)
    event_id = post_resp.json()["id"]
    # Envie um objeto com campo inválido ou tipo totalmente inválido
    resp = client.patch(f"/api/v1/eventos/{event_id}", json={"not_expected_field": 123}, headers=auth_header)
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    # assert detail == "Nenhum campo válido para atualização."
    assert any(err["type"] == "extra_forbidden" for err in detail)

@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_update_event_type_valid(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido']):
    """PATCH deve aceitar EventUpdate válido e alterar apenas os campos enviados."""
    # --- 1. fixa o repositório (singleton em memória) ---
    repo_singleton = InMemoryEventRepo()
    app.dependency_overrides[provide_event_repo] = lambda: repo_singleton

    try:
        # --- 2. cria um evento ---
        post = client.post("/api/v1/eventos", json=event, headers=auth_header)
        assert post.status_code == 201
        event_id = post.json()["id"]

        # --- 3. envia PATCH parcial ---
        patch_body = {"description": "Descrição atualizada."}
        patch = client.patch(
            f"/api/v1/eventos/{event_id}",
            json=patch_body,
            headers=auth_header,
        )
        assert patch.status_code == 200

        # --- 4. valida resultado ---
        body = patch.json()
        assert body["description"] == "Descrição atualizada."
        assert body["title"] == "Concerto De Jazz"
    finally:
        # limpa override para não interferir em outros testes
        app.dependency_overrides.pop(provide_event_repo, None)

@pytest.mark.parametrize("n,skip,limit", [(30,0,10), (30,10,10), (5,0,10)])
def test_pagination_works_correctly(client: TestClient, auth_header: dict[str, str], repo, n: Literal[30] | Literal[5], skip: Literal[0] | Literal[10], limit: Literal[10]):
    # cria n eventos dummy
    for _ in range(n):
        repo.add(EventCreate(...))   # use factory/faker
    resp = client.get(f"/api/v1/eventos?skip={skip}&limit={limit}", headers=auth_header)
    assert resp.status_code == 200
    assert len(resp.json()) == min(limit, max(0, n-skip))

def test_list_events_with_pagination(repo):
    # cria 3 eventos de teste
    for i in range(3):
        repo.add(EventCreate(title=f"E{i}", description="...", event_date=datetime.now(timezone.utc),
                             city="Recife", participants=[]))
    page = repo.list_partial(skip=1, limit=1)
    assert len(page) == 1

@pytest.mark.parametrize("csv_file", ["valido"], indirect=True)
def test_upload_csv_sucesso(client_autenticado: TestClient, csv_file):
    file, filename = csv_file
    response = client_autenticado.post(
        "/api/v1/eventos/upload",
        files={"file": (filename, file, "text/csv")}
    )

    assert response.status_code == 201
    resultado = response.json()
    assert resultado["status"] == "finalizado"
    assert resultado["total"] == 1

@pytest.mark.parametrize("csv_file", ["invalido"], indirect=True)
def test_upload_csv_falha(client_autenticado: TestClient, csv_file):
    file, filename = csv_file
    response = client_autenticado.post(
        "/api/v1/eventos/upload",
        files={"file": (filename, file, "text/csv")}
    )

    assert response.status_code == 400
    resultado = response.json()
    assert resultado["detail"] == "Nenhum evento válido foi importado"

def test_upload_csv_sem_arquivo(client_autenticado: TestClient):
    response = client_autenticado.post(
        "/api/v1/eventos/upload"
    )
    assert response.status_code == 422  # FastAPI valida se arquivo é obrigatório

def test_upload_csv_erro_decodificacao(client_autenticado: TestClient):
    conteudo_invalido = b'\xff\xff\xff\xff'
    response = client_autenticado.post(
        "/api/v1/eventos/upload",
        files={"file": ("erro.csv", BytesIO(conteudo_invalido), "text/csv")}
    )
    assert response.status_code == 400
    resultado = response.json()
    assert resultado["detail"] == "Nenhum evento válido foi importado"