# tests/unit/test_eventos.py

import pytest
from datetime import datetime

def test_obter_local_info(client_autenticado):
    response = client_autenticado.get("/api/v1/local_info", params={"location_name": "auditorio central"})
    assert response.status_code == 200
    assert response.json()["location_name"] == "auditorio central"

def test_obter_forecast_info(client_autenticado):
    response = client_autenticado.get("/api/v1/forecast_info", params={
        "city": "Recife",
        "date": datetime.now().isoformat()
    })
    assert response.status_code == 200
    assert "temperature" in response.json()

def test_obter_forecast_info_nao_encontrada(client_autenticado):
    response = client_autenticado.get("/api/v1/forecast_info", params={
        "city": "cidade_inexistente_zzz",
        "date": "2030-01-01T00:00:00"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Previsão não encontrada"

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_criar_evento_valido(client_autenticado, evento):
    response = client_autenticado.post("/api/v1/eventos", json=evento)
    assert response.status_code == 201
    assert response.json()["title"].lower() == evento["title"].lower()

@pytest.mark.parametrize("evento", ["evento_invalido"], indirect=True)
def test_criar_evento_invalido(client_autenticado, evento):
    response = client_autenticado.post("/api/v1/eventos", json=evento)
    assert response.status_code == 422

def test_listar_eventos(client_autenticado):
    response = client_autenticado.get("/api/v1/eventos")
    # Pode ser 200 ou 404, dependendo se já apagou ou não
    assert response.status_code in (200, 404)
