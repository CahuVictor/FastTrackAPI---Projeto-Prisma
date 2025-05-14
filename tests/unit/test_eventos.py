# cobre operações básicas (criar, listar, buscar, deletar individual).

# from fastapi.testclient import TestClient
# from app.main import app

# client = TestClient(app)

# # Dados válidos para criação
# evento_valido = {
#     "title": "Concerto De Jazz",
#     "description": "Uma apresentação musical.",
#     "event_date": "2025-06-01T20:00:00",
#     "participants": ["Alice", "Bruno"],
#     "local_info": {
#         "location_name": "auditório central",
#         "capacity": 200,
#         "venue_type": "Auditorio",
#         "is_accessible": True,
#         "address": "Rua Exemplo, 123",
#         "past_events": ["Feira de Tecnologia", "Hackathon 2024"]
#     }
# }

# # Dados inválidos (faltando campo obrigatório)
# evento_invalido = {
#     "title": "Evento Incompleto",
#     "event_date": "2025-06-01T20:00:00",
#     "participants": ["Zé"]
# }

import pytest

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_criar_evento_valido(client, evento):
# def test_criar_evento_valido():
#     response = client.post("/api/v1/eventos", json=evento_valido)
    response = client.post("/api/v1/eventos", json=evento)
    assert response.status_code == 200
#     evento["title"] quando salvo no evento sofre a transformação .title()
#     assert response.json()["title"] == evento["title"].title()
    assert response.json()["title"].lower() == evento["title"].lower()

@pytest.mark.parametrize("evento", ["evento_invalido"], indirect=True)
def test_criar_evento_invalido(client, evento):
# def test_criar_evento_invalido():
    response = client.post("/api/v1/eventos", json=evento)
    assert response.status_code == 422  # Unprocessable Entity

def test_listar_eventos(client):
# def test_listar_eventos():
    response = client.get("/api/v1/eventos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_obter_evento_por_id(client, evento):
# def test_obter_evento_por_id():
#     # cria um evento antes
#     post_response = client.post("/api/v1/eventos", json=evento_valido)
    post_response = client.post("/api/v1/eventos", json=evento)
    evento_id = post_response.json()["id"]
    response = client.get(f"/api/v1/eventos/{evento_id}")
    assert response.status_code == 200
    assert response.json()["id"] == evento_id

def test_obter_evento_inexistente(client):
# def test_obter_evento_inexistente():
    response = client.get("/api/v1/eventos/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Evento não encontrado"

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_deletar_evento_por_id(client, evento):
# def test_deletar_evento_por_id():
#     post_response = client.post("/api/v1/eventos", json=evento_valido)
    post_response = client.post("/api/v1/eventos", json=evento)
    evento_id = post_response.json()["id"]
    response = client.delete(f"/api/v1/eventos/{evento_id}")
    assert response.status_code == 200
    assert "mensagem" in response.json()
