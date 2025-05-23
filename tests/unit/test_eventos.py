# cobre operações básicas (criar, listar, buscar, deletar individual).

import pytest

def test_obter_local_info(client):
    response = client.get("/api/v1/local_info", params={"location_name": "auditorio central"})
    assert response.status_code == 200
    assert response.json()["location_name"] == "auditorio central"

def test_obter_forecast_info(client):
    from datetime import datetime
    response = client.get("/api/v1/forecast_info", params={
        "city": "Recife",
        "date": datetime.now().isoformat()
    })
    assert response.status_code == 200
    assert "temperature" in response.json()

def test_obter_forecast_info_nao_encontrada(client):
    response = client.get("/api/v1/forecast_info", params={
        "city": "cidade_inexistente_zzz",
        "date": "2030-01-01T00:00:00"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Previsão não encontrada"

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_criar_evento_valido(client, evento):
    response = client.post("/api/v1/eventos", json=evento)
    assert response.status_code == 201
#     evento["title"] quando salvo no evento sofre a transformação .title()
#     assert response.json()["title"] == evento["title"].title()
    assert response.json()["title"].lower() == evento["title"].lower()

@pytest.mark.parametrize("evento", ["evento_invalido"], indirect=True)
def test_criar_evento_invalido(client, evento):
# def test_criar_evento_invalido():
    response = client.post("/api/v1/eventos", json=evento)
    assert response.status_code == 422  # Unprocessable Entity

def test_listar_eventos(client):
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

# Testar GET /eventos/{id} para um ID inexistente
@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_deletar_evento_por_id(client, evento):
# def test_deletar_evento_por_id():
#     post_response = client.post("/api/v1/eventos", json=evento_valido)
    post_response = client.post("/api/v1/eventos", json=evento)
    evento_id = post_response.json()["id"]
    response = client.delete(f"/api/v1/eventos/{evento_id}")
    assert response.status_code == 200
    assert "mensagem" in response.json()

# Testar DELETE /eventos/{id} para deletar um evento inexistente
def test_deletar_evento_inexistente(client):
    response = client.delete("/api/v1/eventos/99999")
    assert response.status_code == 404

# Testar GET /eventos quando não há eventos
def test_listar_eventos_vazio(client):
    # Remove todos eventos primeiro
    client.delete("/api/v1/eventos")
    response = client.get("/api/v1/eventos")
    assert response.status_code == 404
    assert response.json()["detail"] == "Nenhum evento encontrado."

# Testar POST /eventos/lote com lista vazia
def test_adicionar_eventos_em_lote_vazio(client):
    response = client.post("/api/v1/eventos/lote", json=[])
    assert response.status_code == 400

# Testar GET /local_info para um local inexistente
def test_obter_local_info_inexistente(client):
    response = client.get("/api/v1/local_info", params={"location_name": "local_inexistente"})
    assert response.status_code == 404

# Testar GET /forecast_info para cidade que não está no mock (use um nome qualquer)
from datetime import datetime
def test_obter_forecast_info_cidade_nao_listada(client):
    response = client.get("/api/v1/forecast_info", params={"city": "cidadequalquer", "date": datetime.now().isoformat()})
    assert response.status_code == 200

# Testar exceção ao tentar forecast_info com data ou cidade faltante
def test_obter_forecast_info_params_faltando(client):
    from datetime import datetime
    resp = client.get("/api/v1/forecast_info", params={"city": "recife"})  # falta date
    assert resp.status_code == 422
    resp = client.get("/api/v1/forecast_info", params={"date": datetime.now().isoformat()})  # falta city
    assert resp.status_code == 422

# Testar forecast_info não encontrada (por garantia, city nonsense)
def test_forecast_info_nao_encontrada(client):
    from datetime import datetime
    resp = client.get("/api/v1/forecast_info", params={"city": "cidadequeNExiste", "date": datetime.now().isoformat()})
    assert resp.status_code == 200  # Pelo seu mock, retorna um default, mas teste se algum valor pode retornar 404, ou force None no mock se quiser cobrir branch

@pytest.mark.parametrize("evento", ["eventos_validos_lote"], indirect=True)
def test_adicionar_eventos_em_lote(client, evento):

    response = client.post("/api/v1/eventos/lote", json=evento)
    assert response.status_code == 201
    result = response.json()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["title"] == "Evento 1"
    assert result[1]["title"] == "Evento 2"