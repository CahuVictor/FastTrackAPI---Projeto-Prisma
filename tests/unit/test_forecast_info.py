# tests/test_forecast_info.py
import pytest

from datetime import datetime

from app.main import app
from app.deps import provide_forecast_service


def test_obter_forecast_info(client, auth_header, data_agora_iso):
    resp = client.get(
        "/api/v1/forecast_info",
        params={"city": "Recife", "date": data_agora_iso},
        headers=auth_header,
    )
    assert resp.status_code == 200
    assert "temperature" in resp.json()


def test_obter_forecast_info_nao_encontrada(client, auth_header):
    resp = client.get(
        "/api/v1/forecast_info",
        params={"city": "cidade_inexistente_zzz", "date": "2030-01-01T00:00:00"},
        headers=auth_header,
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Previsão não encontrada"

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_atualizar_forecast_info_com_erro(client, auth_header, evento):
    """
    Força erro no serviço de forecast para cobrir o branch de exceção.
    """
    def fake_forecast_service():
        class _Fake:
            def get_by_city_and_datetime(self, *_):
                raise Exception("erro simulado")
        return _Fake()

    # override
    app.dependency_overrides[provide_forecast_service] = fake_forecast_service

    # cria evento
    post = client.post("/api/v1/eventos", json=evento, headers=auth_header)
    assert post.status_code == 201
    evento_id = post.json()["id"]

    # tenta atualizar forecast → deve falhar
    resp = client.patch(f"/api/v1/eventos/{evento_id}/forecast_info", headers=auth_header)
    assert resp.status_code in (502, 404)
    assert resp.json()["detail"] == "Erro ao obter previsão do tempo"

    # limpa override
    app.dependency_overrides = {}

def test_obter_forecast_info(client, auth_header, dt_now_iso):
    resp = client.get("/api/v1/forecast_info",
        params={
            "city": "Recife",
            "date": dt_now_iso
        },
        headers=auth_header
    )
    assert resp.status_code == 200
    assert "temperature" in resp.json()

def test_obter_forecast_info_nao_encontrada(client, auth_header):
    resp = client.get(
        "/api/v1/forecast_info",
        params={
            "city": "cidade_inexistente_zzz",
            "date": "2030-01-01T00:00:00"
        },
        headers=auth_header
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Previsão não encontrada"

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_atualizar_forecast_info(client, auth_header, evento):
    post_resp = client.post("/api/v1/eventos", json=evento, headers=auth_header)
    evento_id = post_resp.json()["id"]
    resp = client.patch(f"/api/v1/eventos/{evento_id}/forecast_info", headers=auth_header)
    assert resp.status_code == 200
    assert "forecast_info" in resp.json()

# Testar PATCH /eventos/{id}/forecast_info para evento inexistente
def test_atualizar_forecast_info_inexistente(client, auth_header):
    resp = client.patch("/api/v1/eventos/99999/forecast_info", headers=auth_header)
    assert resp.status_code == 404

# Simular erro na atualização de forecast_info (try/except de forecast)
@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_atualizar_forecast_info_com_erro(client, auth_header, evento):
    def fake_forecast_service():
        class FakeService:
            def get_by_city_and_datetime(self, city, date):
                raise Exception("erro simulado")
        return FakeService()
    # Override a dependência
    from app.deps import provide_forecast_service
    app.dependency_overrides[provide_forecast_service] = fake_forecast_service
    
    post_resp = client.post("/api/v1/eventos", json=evento, headers=auth_header)
    assert post_resp.status_code == 201
    evento_id = post_resp.json()["id"]
    
    try:
        resp = client.patch(f"/api/v1/eventos/{evento_id}/forecast_info", headers=auth_header)
        # Mesmo com erro, deve continuar funcionando, forecast_info fica None ou não muda
        assert resp.status_code in (502, 404)
        assert resp.json()["detail"] == "Erro ao obter previsão do tempo"
        # assert resp.json()["forecast_info"] is None or resp.json()["forecast_info"] == {}
    finally:
        # Restaura função original
        app.dependency_overrides = {}

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_criar_evento_forecast_exception(client, auth_header, evento):
    def fake_forecast_service():
        class FakeService:
            def get_by_city_and_datetime(self, city, date):
                raise Exception("erro simulado")
        return FakeService()
    app.dependency_overrides[provide_forecast_service] = fake_forecast_service

    resp = client.post("/api/v1/eventos", json=evento, headers=auth_header)
    assert resp.status_code == 201
    result = resp.json()
    assert result["forecast_info"] is None

    app.dependency_overrides = {}