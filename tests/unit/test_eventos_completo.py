# tests/unit/test_eventos_completo.py
# cobre rotas de substituição, concatenação, atualização parcial, etc.

import pytest
from app.main import app
from app.deps import provide_forecast_service

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_substituir_todos_os_eventos(client_autenticado, evento):
# def test_substituir_todos_os_eventos():
#     novo_evento = evento_valido.copy()
#     novo_evento["title"] = "Evento Substituto"
    evento["title"] = "Evento Substituto"
    response = client_autenticado.put("/api/v1/eventos", json=[evento])
#     response = client_autenticado.put("/api/v1/eventos", json=[novo_evento])
    assert response.status_code == 200
#     assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Evento Substituto"

# Testar PUT /eventos/{id} para substituir um evento inexistente
@pytest.mark.parametrize("evento", ["evento_valido_com_id_e_forecast"], indirect=True)
def test_substituir_evento_inexistente(client_autenticado, evento):
    response = client_autenticado.put("/api/v1/eventos/99999", json=evento)
    assert response.status_code == 404

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_substituir_evento_por_id(client_autenticado, evento):
# def test_substituir_evento_por_id():
    # cria um evento
#     post_response = client_autenticado.post("/api/v1/eventos", json=evento_valido)
    post_response = client_autenticado.post("/api/v1/eventos", json=evento)
    evento_id = post_response.json()["id"]
    evento["title"] = "Novo Título"
#     novo_evento = evento_valido.copy()
#     novo_evento["title"] = "Novo Título"
#     novo_evento["local_info"] = evento_valido["local_info"]
#     response = client_autenticado.put(f"/api/v1/eventos/{evento_id}", json=novo_evento)
    response = client_autenticado.put(f"/api/v1/eventos/{evento_id}", json=evento)
    assert response.status_code == 200
    assert response.json()["title"] == "Novo Título"

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_deletar_todos_os_eventos(client_autenticado, evento):
# def test_deletar_todos_os_eventos():
#     client_autenticado.post("/api/v1/eventos", json=evento_valido)
    client_autenticado.post("/api/v1/eventos", json=evento)
    response = client_autenticado.delete("/api/v1/eventos")
    assert response.status_code == 200
    assert response.json()["mensagem"].startswith("Todos os eventos foram apagados")

# @pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
# def test_concatenar_eventos(client_autenticado, evento):
# # def test_concatenar_eventos():
# #     novo_evento = evento_valido.copy()
# #     response = client_autenticado.patch("/api/v1/eventos", json=[novo_evento])
#     response = client_autenticado.patch("/api/v1/eventos", json=[evento])
#     assert response.status_code == 200
#     assert len(response.json()) >= 1

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_atualizar_local_info(client_autenticado, evento):
    post_response = client_autenticado.post("/api/v1/eventos", json=evento)
    evento_id = post_response.json()["id"]
    atualizacao = {
        "capacity": 999,
        "manually_edited": True  # Obrigatório!
    }
    response = client_autenticado.patch(f"/api/v1/eventos/{evento_id}/local_info", json=atualizacao)
    assert response.status_code == 200
    assert response.json()["local_info"]["capacity"] == 999
    assert response.json()["local_info"]["manually_edited"] is True

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_atualizar_forecast_info(client_autenticado, evento):
    post_response = client_autenticado.post("/api/v1/eventos", json=evento)
    evento_id = post_response.json()["id"]
    response = client_autenticado.patch(f"/api/v1/eventos/{evento_id}/forecast_info")
    assert response.status_code == 200
    assert "forecast_info" in response.json()

# Testar PATCH /eventos/{id} para atualizar um evento inexistente
def test_atualizar_evento_inexistente(client_autenticado):
    atualizacao = {"title": "Novo Título"}
    response = client_autenticado.patch("/api/v1/eventos/99999", json=atualizacao)
    assert response.status_code == 404

# Testar PUT /eventos com lista vazia
def test_substituir_todos_os_eventos_vazio(client_autenticado):
    response = client_autenticado.put("/api/v1/eventos", json=[])
    assert response.status_code == 400

# Testar PATCH /eventos/{id}/local_info para evento inexistente
def test_atualizar_local_info_inexistente(client_autenticado):
    atualizacao = {"capacity": 100, "manually_edited": True}
    response = client_autenticado.patch("/api/v1/eventos/99999/local_info", json=atualizacao)
    assert response.status_code == 404

# Testar PATCH /eventos/{id}/forecast_info para evento inexistente
def test_atualizar_forecast_info_inexistente(client_autenticado):
    response = client_autenticado.patch("/api/v1/eventos/99999/forecast_info")
    assert response.status_code == 404

# Simular erro na atualização de forecast_info (try/except de forecast)
def test_atualizar_forecast_info_com_erro(client_autenticado):
    def fake_forecast_service():
        class FakeService:
            def get_by_city_and_datetime(self, city, date):
                raise Exception("erro simulado")
        return FakeService()
    # Override a dependência
    from app.deps import provide_forecast_service
    app.dependency_overrides[provide_forecast_service] = fake_forecast_service
    
    # Crie o evento e obtenha o evento_id
    evento = {
        "title": "Evento Teste",
        "description": "Teste sem forecast.",
        "event_date": "2025-06-01T20:00:00",
        "city": "Recife",
        "participants": [],
        "local_info": {
            "location_name": "auditório central",
            "capacity": 100,
            "venue_type": "Auditorio",
            "is_accessible": True,
            "address": "Rua Principal, 1",
            "past_events": [],
            "manually_edited": False
        }
    }
    post_resp = client_autenticado.post("/api/v1/eventos", json=evento)
    assert post_resp.status_code == 201
    evento_id = post_resp.json()["id"]
    
    try:
        resp = client_autenticado.patch(f"/api/v1/eventos/{evento_id}/forecast_info")
        # Mesmo com erro, deve continuar funcionando, forecast_info fica None ou não muda
        assert resp.status_code == 502
        assert resp.json()["detail"] == "Erro ao obter previsão do tempo"
        # assert resp.json()["forecast_info"] is None or resp.json()["forecast_info"] == {}
    finally:
        # Restaura função original
        app.dependency_overrides = {}

# Testar erro de validação em update_event (try/except do update_event)
@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_update_event_validationerror(client_autenticado, evento):
    from app.api.v1.endpoints import eventos as eventos_module
    from pydantic import ValidationError

    # Cria evento
    post = client_autenticado.post("/api/v1/eventos", json=evento)
    evento_id = post.json()["id"]

    # Envie update inválido para local_info (ex: capacity string)
    atualizacao = {"capacity": "invalido", "manually_edited": True}
    resp = client_autenticado.patch(f"/api/v1/eventos/{evento_id}/local_info", json=atualizacao)
    assert resp.status_code == 422
    # Detalhe do erro pode ser validado aqui se quiser

# Testar fallback do update_event (branch 'else' no update_event)
@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_update_event_fallback_branch(client_autenticado, evento):
    # cria evento
    post = client_autenticado.post("/api/v1/eventos", json=evento)
    evento_id = post.json()["id"]

    from app.api.v1.endpoints import eventos as eventos_module

    # Chame diretamente update_event com um attr estranho
    ev = eventos_module.eventos_db[evento_id]
    class DummyUpdate:
        def model_dump(self, exclude_unset=True):
            return {"fake": "field"}
    # # Não deve acontecer em produção, mas cobre o else do branch
    # eventos_module.update_event(ev, DummyUpdate(), attr='not_existing_field')
    # # Se não der erro, cobre o else do branch (fallback)
    
    # Deve levantar AttributeError (ou ValidationError, dependendo do caminho)
    with pytest.raises(AttributeError):
        eventos_module.update_event(ev, DummyUpdate(), attr='not_existing_field')

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
def test_atualizar_evento_tipo_invalido(client_autenticado, evento):
    # Crie um evento antes
    post_response = client_autenticado.post("/api/v1/eventos", json=evento)
    evento_id = post_response.json()["id"]
    # Envie um objeto com campo inválido ou tipo totalmente inválido
    response = client_autenticado.patch(f"/api/v1/eventos/{evento_id}", json={"not_expected_field": 123})
    assert response.status_code == 400
    assert response.json()["detail"] == "Nenhum campo válido para atualização."

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_atualizar_evento_tipo_valido(client_autenticado, evento):
    # Crie um evento antes
    post_resp = client_autenticado.post("/api/v1/eventos", json=evento)
    assert post_resp.status_code == 201
    evento_id = post_resp.json()["id"]

    # 2. PATCH com um campo diferente
    atualizacao = {"description": "Descrição atualizada."}
    patch_resp = client_autenticado.patch(f"/api/v1/eventos/{evento_id}", json=atualizacao)
    assert patch_resp.status_code == 200

    # 3. Confira que mudou
    evento_resp = patch_resp.json()
    assert evento_resp["description"] == "Descrição atualizada."
    assert evento_resp["title"] == "Concerto De Jazz"

def test_criar_evento_forecast_exception(client_autenticado, monkeypatch):
    def fake_forecast_service():
        class FakeService:
            def get_by_city_and_datetime(self, city, date):
                raise Exception("erro simulado")
        return FakeService()
    app.dependency_overrides[provide_forecast_service] = fake_forecast_service

    evento = {
        "title": "Evento Teste",
        "description": "Teste sem forecast.",
        "event_date": "2025-06-01T20:00:00",
        "city": "Recife",
        "participants": [],
        "local_info": {
            "location_name": "auditório central",
            "capacity": 100,
            "venue_type": "Auditorio",
            "is_accessible": True,
            "address": "Rua Principal, 1",
            "past_events": [],
            "manually_edited": False
        }
    }

    resp = client_autenticado.post("/api/v1/eventos", json=evento)
    assert resp.status_code == 201
    result = resp.json()
    assert result["forecast_info"] is None

    app.dependency_overrides = {}