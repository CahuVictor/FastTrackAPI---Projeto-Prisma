# tests/test_forecast_info.py
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta, timezone

from app.main import app
from app.deps import provide_forecast_service
from app.services.forecast import atualizar_forecast_em_background
from app.utils.patch import should_update_forecast, update_event_forecast, update_event
from app.schemas.event_create import EventResponse
from app.schemas.event_update import ForecastInfoUpdate, EventUpdate

# TODO Corrigir endpoint para habilitar os testes
# def test_get_forecast_info(client, auth_header, dt_now_iso):
#     resp = client.get("/api/v1/events/forecast_info",
#         params={
#             "city": "Recife",
#             "date": dt_now_iso
#         },
#         headers=auth_header
#     )
#     assert resp.status_code == 200
#     assert "temperature" in resp.json()

# def test_get_forecast_info_nao_encontrada(client, auth_header):
#     resp = client.get(
#         "/api/v1/events/forecast_info",
#         params={
#             "city": "cidade_inexistente_zzz",
#             "date": "2030-01-01T00:00:00"
#         },
#         headers=auth_header
#     )
#     assert resp.status_code == 404
#     assert resp.json()["detail"] == "Previsão não encontrada"

# Simular erro na atualização de forecast_info (try/except de forecast)
@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_update_forecast_info_error(client, auth_header, event):
    """
    Força erro no serviço de forecast para cobrir o branch de exceção.
    
    Mesmo que o serviço de forecast esteja com erro,
    a rota deve apenas agendar a tarefa e responder com 200.
    O erro acontecerá no background e será logado.
    """
    def fake_forecast_service():
        class _Fake:
            def get_by_city_and_datetime(self, *_):
                raise Exception("erro simulado")
        return _Fake()

    # override
    app.dependency_overrides[provide_forecast_service] = fake_forecast_service

    # cria evento
    post = client.post("/api/v1/events", json=event, headers=auth_header)
    assert post.status_code == 201
    evento_id = post.json()["id"]

    # tenta atualizar forecast → deve falhar
    resp = client.patch(f"/api/v1/events/{evento_id}/forecast_info", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Tarefa de atualização de forecast agendada"
    
    # post_resp = client.post("/api/v1/events", json=event, headers=auth_header)
    # assert post_resp.status_code == 201
    # evento_id = post_resp.json()["id"]
    
    # try:
    #     resp = client.patch(f"/api/v1/events/{evento_id}/forecast_info", headers=auth_header)
    #     # Mesmo com erro, deve continuar funcionando, forecast_info fica None ou não muda
    #     assert resp.status_code in (502, 404)
    #     assert resp.json()["detail"] == "Erro ao obter previsão do tempo"
    #     # assert resp.json()["forecast_info"] is None or resp.json()["forecast_info"] == {}
    # finally:
    #     # Restaura função original
    #     app.dependency_overrides = {}

    # limpa override
    app.dependency_overrides = {}

@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_atualizar_forecast_info(client, auth_header, event):
    post_resp = client.post("/api/v1/events", json=event, headers=auth_header)
    evento_id = post_resp.json()["id"]
    resp = client.patch(f"/api/v1/events/{evento_id}/forecast_info", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Tarefa de atualização de forecast agendada"

# Testar PATCH /events/{id}/forecast_info para evento inexistente
def test_atualizar_forecast_info_inexistente(client, auth_header):
    resp = client.patch("/api/v1/events/99999/forecast_info", headers=auth_header)
    assert resp.status_code == 404

@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_criar_evento_forecast_exception(client, auth_header, event):
    def fake_forecast_service():
        class FakeService:
            def get_by_city_and_datetime(self, city, date):
                raise Exception("erro simulado")
        return FakeService()
    app.dependency_overrides[provide_forecast_service] = fake_forecast_service

    resp = client.post("/api/v1/events", json=event, headers=auth_header)
    assert resp.status_code == 201
    result = resp.json()
    assert result["forecast_info"] is None

    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_atualizar_forecast_em_background_com_sucesso(monkeypatch):
    """
    Testa execução direta da função de forecast, simulando repositório e serviço.
    """

    # Mocks
    fake_event = MagicMock()
    fake_event.city = "Recife"
    fake_event.event_date = datetime(2025, 6, 1, 20, 0, tzinfo=timezone.utc)
    fake_event.forecast_info = None

    repo = MagicMock()
    repo.get.return_value = fake_event
    repo.replace_by_id.return_value = None

    forecast = MagicMock()
    forecast.model_dump.return_value = {"temperature": 30, "humidity": 70}

    service = MagicMock()
    service.get_by_city_and_datetime.return_value = forecast

    monkeypatch.setattr("app.services.forecast.provide_forecast_service", lambda: service)
    monkeypatch.setattr("app.services.forecast.provide_event_repo", lambda: repo)

    # Executa
    await atualizar_forecast_em_background(event_id=123)

    repo.get.assert_called_once_with(123)
    service.get_by_city_and_datetime.assert_called_once_with("Recife", fake_event.event_date)
    repo.replace_by_id.assert_called_once()

@pytest.mark.asyncio
async def test_atualizar_forecast_em_background_falha_com_retry(monkeypatch):
    repo = MagicMock()
    repo.get.return_value = MagicMock(city="Recife", event_date=datetime.now(timezone.utc))

    service = MagicMock()
    service.get_by_city_and_datetime.side_effect = Exception("Erro fake")

    monkeypatch.setattr("app.services.forecast.provide_forecast_service", lambda: service)
    monkeypatch.setattr("app.services.forecast.provide_event_repo", lambda: repo)

    await atualizar_forecast_em_background(event_id=1, retries=2, delay=0)

    assert service.get_by_city_and_datetime.call_count == 2

# ------------------ should_update_forecast ------------------

def test_should_update_forecast_none():
    assert should_update_forecast(None) is True


def test_should_update_forecast_old_date():
    forecast = ForecastInfoUpdate(updated_at=datetime.now(timezone.utc) - timedelta(days=2))
    assert should_update_forecast(forecast) is True


def test_should_update_forecast_recent_date():
    forecast = ForecastInfoUpdate(updated_at=datetime.now(timezone.utc) - timedelta(hours=12))
    assert should_update_forecast(forecast) is False

# ------------------ update_event_forecast ------------------

@pytest.mark.parametrize("event", ["evento_valido_com_id"], indirect=True)
def test_update_event_forecast_when_none(event):
    event["forecast_info"] = None
    update = ForecastInfoUpdate(
        temperature=25.0,
        updated_at=datetime.now(timezone.utc)
    )
    event_obj = EventResponse.model_validate(event)
    updated = update_event_forecast(event_obj, update)
    assert updated.forecast_info.temperature == 25.0

@pytest.mark.parametrize("event", ["evento_valido_com_id_e_forecast"], indirect=True)
def test_update_event_forecast_merge(event, forecast_info_update):
    forecast_info_update.weather_main = "Rain"
    event_obj = EventResponse.model_validate(event)
    updated = update_event_forecast(event_obj, forecast_info_update)
    assert updated.forecast_info.weather_main == "Rain"
    assert updated.forecast_info.temperature == 28.0  # herdado do original

# ------------------ update_event ------------------

@pytest.mark.parametrize("event", ["evento_valido_com_id"], indirect=True)
def test_update_event_without_attr(event):
    # converte o dict para um EventResponse válido (que aceita id e local_info como dict)
    event_obj = EventResponse.model_validate(event)
    
    # update só com os campos que podem ser atualizados
    update = EventUpdate(title="Novo título")

    result = update_event(event_obj, update)
    assert result.title == "Novo título"


@pytest.mark.parametrize("event", ["evento_valido_com_id_e_forecast"], indirect=True)
def test_update_event_forecast_info_merge(event):
    event_obj = EventResponse.model_validate(event)
    update = ForecastInfoUpdate(humidity=75, updated_at=datetime.now(timezone.utc))
    updated = update_event(event_obj, update, attr="forecast_info")
    assert updated.forecast_info.humidity == 75


# @pytest.mark.parametrize("event", ["evento_valido_com_id"], indirect=True)
# def test_update_event_local_info_new(event):
#     event["local_info"] = None
#     update = LocalInfoUpdate(city="Olinda")  # supondo que tenha campo city no LocalInfo
#     result = update_event(EventUpdate.model_validate(event), update, attr="local_info")
#     assert result.local_info.city == "Olinda"