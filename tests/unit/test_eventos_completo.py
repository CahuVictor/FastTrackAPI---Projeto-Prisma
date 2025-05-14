# cobre rotas de substituição, concatenação, atualização parcial, etc.

# from fastapi.testclient import TestClient
# from app.main import app
# 
# client = TestClient(app)
# 
# evento_valido = {
#     "title": "Concerto de Jazz",
#     "description": "Uma apresentação musical.",
#     "event_date": "2025-06-01T20:00:00",
#     "participants": ["Alice", "Bruno"],
#     "local_info": {
#         "location_name": "Auditório Central",
#         "capacity": 200,
#         "venue_type": "Auditorio",
#         "is_accessible": True,
#         "address": "Rua Exemplo, 123",
#         "past_events": ["Feira 2023", "Hackathon"]
#     }
# }
#
import pytest

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_substituir_todos_os_eventos(client, evento):
# def test_substituir_todos_os_eventos():
#     novo_evento = evento_valido.copy()
#     novo_evento["title"] = "Evento Substituto"
    evento["title"] = "Evento Substituto"
    response = client.put("/api/v1/eventos", json=[evento])
#     response = client.put("/api/v1/eventos", json=[novo_evento])
    assert response.status_code == 200
#     assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Evento Substituto"

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_substituir_evento_por_id(client, evento):
# def test_substituir_evento_por_id():
    # cria um evento
#     post_response = client.post("/api/v1/eventos", json=evento_valido)
    post_response = client.post("/api/v1/eventos", json=evento)
    evento_id = post_response.json()["id"]
    evento["title"] = "Novo Título"
#     novo_evento = evento_valido.copy()
#     novo_evento["title"] = "Novo Título"
#     novo_evento["local_info"] = evento_valido["local_info"]
#     response = client.put(f"/api/v1/eventos/{evento_id}", json=novo_evento)
    response = client.put(f"/api/v1/eventos/{evento_id}", json=evento)
    assert response.status_code == 200
    assert response.json()["title"] == "Novo Título"

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_deletar_todos_os_eventos(client, evento):
# def test_deletar_todos_os_eventos():
#     client.post("/api/v1/eventos", json=evento_valido)
    client.post("/api/v1/eventos", json=evento)
    response = client.delete("/api/v1/eventos")
    assert response.status_code == 200
    assert response.json()["mensagem"] == "Todos os eventos foram apagados com sucesso"

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_concatenar_eventos(client, evento):
# def test_concatenar_eventos():
#     novo_evento = evento_valido.copy()
#     response = client.patch("/api/v1/eventos", json=[novo_evento])
    response = client.patch("/api/v1/eventos", json=[evento])
    assert response.status_code == 200
    assert len(response.json()) >= 1

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_atualizar_parcial_evento(client, evento):
# def test_atualizar_parcial_evento():
#     post_response = client.post("/api/v1/eventos", json=evento_valido)
    post_response = client.post("/api/v1/eventos", json=evento)
    evento_id = post_response.json()["id"]
    atualizacao = {
#         "local_info": evento_valido["local_info"],
        "local_info": evento["local_info"],
        "forecast_info": {
            "forecast_datetime": "2025-06-01T15:00:00",
            "temperature": 27.5,
            "weather_main": "Clear",
            "weather_desc": "Céu limpo",
            "humidity": 50,
            "wind_speed": 3.2
        }
    }
    response = client.patch(f"/api/v1/eventos/{evento_id}", json=atualizacao)
    json_resp = response.json()
    assert response.status_code == 200
    # assert "evento" in response.json()

    assert json_resp["forecast_info"]["temperature"] == 27.5
    assert json_resp["forecast_info"]["weather_desc"] == "Céu limpo" 
#     assert json_resp["local_info"]["location_name"] == "Auditório Central"
    assert json_resp["local_info"]["location_name"] == evento["local_info"]["location_name"]
    assert json_resp["local_info"]["capacity"] == 200
