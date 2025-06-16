# tests/unit/test_localinfo.py

from typing import Literal
from fastapi.testclient import TestClient
import pytest

# from fastapi import HTTPException
# from pydantic import ValidationError, FieldValidationInfo
# from pydantic import ValidationError

from app.main import app
from app.deps import provide_local_info_service

from app.schemas.local_info import LocalInfo
from app.services.mock_local_info import MockLocalInfoService

def test_get_local_info_endpoint(client: TestClient, auth_header: dict[str, str]):
    resp = client.get(
        "/api/v1/local_info",
        params={"location_name": "auditorio central"},
        headers=auth_header,
    )
    assert resp.status_code == 200
    assert resp.json()["location_name"] == "auditorio central"
    assert "location_name" in resp.json()

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_atualizar_local_info_tipo_invalido_unit(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido_com_id']):
    evento_id = 300
    evento["id"] = evento_id
    client.put("/api/v1/eventos", json=[evento], headers=auth_header)
    # with pytest.raises(HTTPException) as excinfo:
    #     # Passa um dict em vez de LocalInfoUpdate
    #     client.patch(f"/api/v1/eventos/300/local_info", json={"foo": "bar"}, headers=auth_header)
    # assert excinfo.value.status_code == 500
    # assert excinfo.value.detail == "Tipo inválido para LocalInfoUpdate"
    resp = client.patch(f"/api/v1/eventos/{evento_id}/local_info", json={"foo": "bar"}, headers=auth_header)
    assert resp.status_code == 422 # 502 - FastAPI/Pydantic devolve 422 p/ corpo inválido
    assert resp.json()["detail"] == "Erro ao receber dados do Local"
    assert resp.json()["local_info"]["foo"] == "bar"

@pytest.mark.parametrize("evento", ["evento_valido_com_id"], indirect=True)
def test_atualizar_local_info_none_unit(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido_com_id']):
    evento_id = 301
    evento["id"] = evento_id
    client.put("/api/v1/eventos", json=[evento], headers=auth_header)
    # with pytest.raises(HTTPException) as excinfo:
    #     client.patch(f"/api/v1/eventos/301/local_info", json=None, headers=auth_header)
    # assert excinfo.value.status_code == 502
    # assert excinfo.value.detail == "Erro ao receber dados do Local"
    resp = client.patch(f"/api/v1/eventos/{evento_id}/local_info", json=None, headers=auth_header)
    assert resp.status_code == 422 # 502 - FastAPI/Pydantic devolve 422 p/ corpo inválido
    assert resp.json()["detail"] == "Erro ao receber dados do Local"

@pytest.mark.parametrize("evento", ["evento_valido"], indirect=True)
def test_atualizar_local_info(client: TestClient, auth_header: dict[str, str], evento: Literal['evento_valido']):
    post_response = client.post("/api/v1/eventos", json=evento, headers=auth_header)
    evento_id = post_response.json()["id"]
    atualizacao = {
        "capacity": 999,
        "manually_edited": True  # Obrigatório!
    }
    response = client.patch(f"/api/v1/eventos/{evento_id}/local_info", json=atualizacao, headers=auth_header)
    assert response.status_code == 200
    assert response.json()["local_info"]["capacity"] == 999
    assert response.json()["local_info"]["manually_edited"] is True

# Testar PATCH /eventos/{id}/local_info para evento inexistente
def test_atualizar_local_info_inexistente(client: TestClient, auth_header: dict[str, str]):
    atualizacao = {"capacity": 100, "manually_edited": True}
    response = client.patch("/api/v1/eventos/99999/local_info", json=atualizacao, headers=auth_header)
    assert response.status_code == 404

# Testa o serviço diretamente, sem endpoint
def test_servico_mock_local_info_unitario():
    service = MockLocalInfoService()
    info = service.get_by_name("auditório central")
    assert info is not None
    info_none = service.get_by_name("local inexistente 999")
    assert info_none is None

def test_mock_local_info_service_unit(mock_local_info_service: MockLocalInfoService):
    info = mock_local_info_service.get_by_name("auditório central")
    assert info is not None
    info_none = mock_local_info_service.get_by_name("inexistente")
    assert info_none is None

@pytest.mark.parametrize("localinfo", ["localinfo_type_error"], indirect=True)
def test_location_name_validator_typeerror(localinfo: Literal['localinfo_type_error']):
    # with pytest.raises(ValidationError):
    with pytest.raises(TypeError):
        # localinfo
        LocalInfo(**localinfo)

@pytest.mark.parametrize("localinfo", ["localinfo_past_events_type_error"], indirect=True)
def test_past_events_validator_typeerror(localinfo: Literal['localinfo_past_events_type_error']):
    # with pytest.raises(ValidationError):
    with pytest.raises(TypeError):
        # localinfo
        LocalInfo(**localinfo)

@pytest.mark.parametrize("localinfo", ["localinfo_past_events_value_error"], indirect=True)
def test_past_events_validator_valueerror(localinfo: Literal['localinfo_past_events_value_error']):
    # with pytest.raises(ValidationError):
    with pytest.raises(TypeError):
        # localinfo
        LocalInfo(**localinfo)

def fake_local_info_service():
    class FakeLocalInfo:
        def get_by_name(self, location_name):
            return None  # ou qualquer comportamento desejado
    return FakeLocalInfo()

def test_endpoint_com_dependencia_override(client: TestClient, auth_header: dict[str, str]):
    app.dependency_overrides[provide_local_info_service] = fake_local_info_service
    # agora qualquer chamada à rota vai usar esse fake em vez do padrão
    resp = client.get("/api/v1/local_info?location_name=fake", headers=auth_header)
    assert resp.status_code == 404
    app.dependency_overrides = {}  # Limpe sempre após!