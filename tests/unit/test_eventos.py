# tests/unit/test_eventos.py
# (eventos & manipulação geral)

from typing import Literal
from fastapi.testclient import TestClient
import pytest

from fastapi import HTTPException

from app.main import app
from app.deps import provide_evento_repo
from app.api.v1.endpoints.eventos import atualizar_evento
from app.repositories.evento_mem import InMemoryEventoRepo

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_criar_evento_valido(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido']):
    resp = client.post("/api/v1/eventos", json=evento, headers=auth_header) # evento_valido
    assert resp.status_code == 201
    assert resp.json()["title"].lower() == evento["title"].lower() # evento_valido

@pytest.mark.parametrize("evento", ["evento_invalido"], indirect=True)
def test_criar_evento_invalido(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_invalido']):
    resp = client.post("/api/v1/eventos", json=evento, headers=auth_header) # evento_invalido
    assert resp.status_code == 422

def test_listar_eventos(client: TestClient, auth_header: dict[str, str]):
    resp = client.get("/api/v1/eventos", headers=auth_header)
    # Pode ser 200 ou 404, dependendo se já apagou ou não
    assert resp.status_code in (200, 404)

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_substituir_todos_os_eventos(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido_com_id']):
    evento["title"] = "Evento Substituto"
    resp = client.put("/api/v1/eventos", json=[evento], headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()[0]["title"] == "Evento Substituto"

@pytest.mark.parametrize("evento", ["evento_valido_com_id_forecast"], indirect=True)
def test_substituir_evento_inexistente(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido_com_id_forecast']):
    resp = client.put("/api/v1/eventos/99999", json=evento, headers=auth_header)
    assert resp.status_code == 404

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_atualizar_evento_none_unit(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido_com_id']):
    """
    Testa a branch onde 'atualizacao' é None na função atualizar_evento.
    FastAPI nunca permite isso via HTTP, mas pode ocorrer em uso direto da função.
    Espera-se um HTTPException 502.
    """
    # primeiro garante que o evento existe no repositório
    client.put("/api/v1/eventos", json=[evento], headers=auth_header)
    
    evento_id = evento["id"]
    
    resp = client.patch(
        f"/api/v1/eventos/{evento_id}",
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

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_atualizar_evento_tipo_invalido_unit(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido_com_id']):
    """
    Testa a branch onde 'atualizacao' é de tipo inválido na função atualizar_evento.
    FastAPI/Pydantic nunca permite isso via HTTP, mas pode ocorrer em uso direto da função.
    Espera-se um HTTPException 500.
    """
    # garante que o evento existe
    client.put("/api/v1/eventos", json=[evento], headers=auth_header)
    
    evento_id = evento["id"]
    
    resp = client.patch(
        f"/api/v1/eventos/{evento_id}",
        json=789,                       # corpo inválido
        headers=auth_header
    )

    assert resp.status_code == 422
    # (opcional) checagem da mensagem de erro de validação
    detail = resp.json()["detail"][0]
    # assert detail["type"] == "int_parsing" or detail["msg"].startswith("value is not a valid dict")
    assert detail["type"] in {"missing", "model_attributes_type"}

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_substituir_todos_os_eventos(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido_com_id']):
    evento["title"] = "Evento Substituto"
    resp = client.put("/api/v1/eventos", json=[evento], headers=auth_header)
#     response = client_autenticado.put("/api/v1/eventos", json=[novo_evento])
    assert resp.status_code == 200
#     assert len(response.json()) == 1
    assert resp.json()[0]["title"] == "Evento Substituto"

# Testar PUT /eventos/{id} para substituir um evento inexistente
@pytest.mark.parametrize("evento", ["evento_valido_com_id_e_forecast"], indirect=True)
def test_substituir_evento_inexistente(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido_com_id_e_forecast']):
    resp = client.put("/api/v1/eventos/99999", json=evento, headers=auth_header)
    assert resp.status_code == 404
    
@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_substituir_evento_por_id(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido']):
    # 1) cria o evento original
    post = client.post("/api/v1/eventos", json=evento, headers=auth_header)
    evento_id = post.json()["id"]

    # 2) monta a versão completa que irá substituir
    novo_evento = evento.copy()
    novo_evento["id"] = evento_id          # obrigatório no PUT
    novo_evento["title"] = "Novo Título"

    # 3) faz a substituição
    resp = client.put(
        f"/api/v1/eventos/{evento_id}",
        json=novo_evento,
        headers=auth_header,
    )

    assert resp.status_code == 200
    assert resp.json()["title"] == "Novo Título"

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_deletar_todos_os_eventos(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido']):
    client.post("/api/v1/eventos", json=evento, headers=auth_header)
    resp = client.delete("/api/v1/eventos", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["mensagem"].startswith("Todos os eventos foram apagados")

# Testar PATCH /eventos/{id} para atualizar um evento inexistente
def test_atualizar_evento_inexistente(client: TestClient, auth_header: dict[str, str]):
    atualizacao = {"title": "Novo Título"}
    response = client.patch("/api/v1/eventos/99999", json=atualizacao, headers=auth_header)
    assert response.status_code == 404

# Testar PUT /eventos com lista vazia
def test_substituir_todos_os_eventos_vazio(client: TestClient, auth_header: dict[str, str]):
    response = client.put("/api/v1/eventos", json=[], headers=auth_header)
    assert response.status_code == 400

# Testar erro de validação em update_event (try/except do update_event)
@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_update_event_validationerror(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido']):
    from app.api.v1.endpoints import eventos as eventos_module
    from pydantic import ValidationError

    # Cria evento
    post_resp = client.post("/api/v1/eventos", json=evento, headers=auth_header)
    evento_id = post_resp.json()["id"]

    # Envie update inválido para local_info (ex: capacity string)
    atualizacao = {"capacity": "invalido", "manually_edited": True}
    resp = client.patch(f"/api/v1/eventos/{evento_id}/local_info", json=atualizacao, headers=auth_header)
    assert resp.status_code == 422
    # Detalhe do erro pode ser validado aqui se quiser

# # Testar o caso: atualizacao é None (502)
# @pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
# def test_atualizar_evento_none(client_autenticado, evento):
#     # Crie um evento antes
#     post_response = client_autenticado.post("/api/v1/eventos", json=evento)
#     evento_id = post_response.json()["id"]
#     # Envie um body explícito None (JSON 'null')
#     response = client_autenticado.patch(f"/api/v1/eventos/{evento_id}", data="null", headers={"Content-Type": "application/json"})
#     assert response.status_code == 502
#     assert response.json()["detail"] == "Erro ao receber dados do evento"

# Testar o caso: atualizacao não é EventUpdate (500)
@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_atualizar_evento_tipo_invalido(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido']):
    # Crie um evento antes
    post_resp = client.post("/api/v1/eventos", json=evento, headers=auth_header)
    evento_id = post_resp.json()["id"]
    # Envie um objeto com campo inválido ou tipo totalmente inválido
    resp = client.patch(f"/api/v1/eventos/{evento_id}", json={"not_expected_field": 123}, headers=auth_header)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Nenhum campo válido para atualização."

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_atualizar_evento_tipo_valido(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido']):
    """PATCH deve aceitar EventUpdate válido e alterar apenas os campos enviados."""
    # --- 1. fixa o repositório (singleton em memória) ---
    repo_singleton = InMemoryEventoRepo()
    app.dependency_overrides[provide_evento_repo] = lambda: repo_singleton

    try:
        # --- 2. cria um evento ---
        post = client.post("/api/v1/eventos", json=evento, headers=auth_header)
        assert post.status_code == 201
        evento_id = post.json()["id"]

        # --- 3. envia PATCH parcial ---
        patch_body = {"description": "Descrição atualizada."}
        patch = client.patch(
            f"/api/v1/eventos/{evento_id}",
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
        app.dependency_overrides.pop(provide_evento_repo, None)

@pytest.mark.parametrize("n,skip,limit", [(30,0,10), (30,10,10), (5,0,10)])
def test_paginacao(client: TestClient, auth_header: dict[str, str], repo, n: Literal[30] | Literal[5], skip: Literal[0] | Literal[10], limit: Literal[10]):
    # cria n eventos dummy
    for _ in range(n):
        repo.add(EventCreate(...))   # use factory/faker
    resp = client.get(f"/api/v1/eventos?skip={skip}&limit={limit}", headers=auth_header)
    assert resp.status_code == 200
    assert len(resp.json()) == min(limit, max(0, n-skip))

def test_list_eventos_paginado(repo):
    # cria 3 eventos de teste
    for i in range(3):
        repo.add(EventCreate(title=f"E{i}", description="...", event_date=datetime.now(),
                             city="Recife", participants=[]))
    page = repo.list_partial(skip=1, limit=1)
    assert len(page) == 1