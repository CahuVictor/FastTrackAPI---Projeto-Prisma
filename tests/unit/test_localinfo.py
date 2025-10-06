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

from app.constants.routes import (
    EVENTS_PREFIX,
    EVENTS_LOCAL_INFO_ROUTE,
    EVENTS_DETAIL_LOCAL_INFO_ROUTE,
    EVENTS_LOCAL_INFO_BY_NAME_ROUTE,
)

def test_get_local_info_endpoint(client: TestClient, auth_header: dict[str, str]):
    resp = client.get(
        EVENTS_LOCAL_INFO_ROUTE,
        params={"location_name": "auditorio central"},
        headers=auth_header,
    )
    assert resp.status_code == 200
    assert resp.json()["location_name"] == "auditorio central"
    assert "location_name" in resp.json()

@pytest.mark.parametrize("event", ["evento_valido_com_id"], indirect=True)
def test_update_local_info_type_invalid_unit(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido_com_id']):
    evento_id = 300
    event["id"] = evento_id
    client.put(EVENTS_PREFIX, json=[event], headers=auth_header)
    # with pytest.raises(HTTPException) as excinfo:
    #     # Passa um dict em vez de LocalInfoUpdate
    #     client.patch(EVENTS_DETAIL_LOCAL_INFO_ROUTE(300), json={"foo": "bar"}, headers=auth_header)
    # assert excinfo.value.status_code == 500
    # assert excinfo.value.detail == "Tipo inválido para LocalInfoUpdate"
    resp = client.patch(EVENTS_DETAIL_LOCAL_INFO_ROUTE(evento_id), json={"foo": "bar"}, headers=auth_header)
    assert resp.status_code == 422 # 502 - FastAPI/Pydantic devolve 422 p/ corpo inválido
    detail = resp.json()["detail"]
    # deve vir a lista gerada pelo Pydantic/FastAPI
    assert isinstance(detail, list)
    assert any(err.get("type") == "extra_forbidden" for err in detail)
    # assert resp.json()["detail"] == "Erro ao receber dados do Local"
    # assert resp.json()["local_info"]["foo"] == "bar"

@pytest.mark.parametrize("event", ["evento_valido_com_id"], indirect=True)
def test_update_local_info_none_unit(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido_com_id']):
    evento_id = 301
    event["id"] = evento_id
    client.put(EVENTS_PREFIX, json=[event], headers=auth_header)
    # with pytest.raises(HTTPException) as excinfo:
    #     client.patch(EVENTS_DETAIL_LOCAL_INFO_ROUTE(301), json=None, headers=auth_header)
    # assert excinfo.value.status_code == 502
    # assert excinfo.value.detail == "Erro ao receber dados do Local"
    resp = client.patch(EVENTS_DETAIL_LOCAL_INFO_ROUTE(evento_id), json=None, headers=auth_header)
    assert resp.status_code == 422 # 502 - FastAPI/Pydantic devolve 422 p/ corpo inválido
    assert resp.json()["detail"] == "Erro ao receber dados do Local"
    # detail = resp.json()["detail"]
    # assert isinstance(detail, list)
    # assert detail[0]["msg"] == "Field required"         # ou qualquer validação que prefira

@pytest.mark.parametrize("event", ["evento_valido"], indirect=True)
def test_update_local_info(client: TestClient, auth_header: dict[str, str], event: Literal['evento_valido']):
    post_response = client.post(EVENTS_PREFIX, json=event, headers=auth_header)
    evento_id = post_response.json()["id"]
    update = {
        "capacity": 999,
        "manually_edited": True  # Obrigatório!
    }
    response = client.patch(EVENTS_DETAIL_LOCAL_INFO_ROUTE(evento_id), json=update, headers=auth_header)
    assert response.status_code == 200
    assert response.json()["local_info"]["capacity"] == 999
    assert response.json()["local_info"]["manually_edited"] is True

# Testar PATCH /eventos/{id}/local_info para evento inexistente
def test_update_nonexistent_local_info(client: TestClient, auth_header: dict[str, str]):
    update = {"capacity": 100, "manually_edited": True}
    response = client.patch(EVENTS_DETAIL_LOCAL_INFO_ROUTE(99999), json=update, headers=auth_header)
    assert response.status_code == 404

# ---------------------------------------------------------------------------
# Testes que chamam diretamente o serviço assíncrono
# ---------------------------------------------------------------------------

# Testa o serviço diretamente, sem endpoint
@pytest.mark.anyio
async def test_service_mock_local_info_unit() -> None:
    service = MockLocalInfoService()
    
    info = await service.get_by_name("auditório central")
    assert info is not None
    
    info_none = await service.get_by_name("local inexistente 999")
    assert info_none is None

@pytest.mark.anyio
async def test_mock_local_info_service_unit(mock_local_info_service: MockLocalInfoService):
    info = await mock_local_info_service.get_by_name("auditório central")
    assert info is not None
    
    info_none = await mock_local_info_service.get_by_name("inexistente")
    assert info_none is None

@pytest.mark.parametrize("localinfo", ["localinfo_type_error"], indirect=True)
def test_location_name_validator_typeerror(localinfo: Literal['localinfo_type_error']):
    # with pytest.raises(ValidationError):
    with pytest.raises(TypeError):
        # localinfo
        LocalInfo(**localinfo)

# @pytest.mark.parametrize("localinfo", ["localinfo_past_events_type_error"], indirect=True)
# def test_past_events_validator_typeerror(localinfo: Literal['localinfo_past_events_type_error']):
#     # with pytest.raises(ValidationError):
#     with pytest.raises(TypeError):
#         # localinfo
#         LocalInfo(**localinfo)

# @pytest.mark.parametrize("localinfo", ["localinfo_past_events_value_error"], indirect=True)
# def test_past_events_validator_valueerror(localinfo: Literal['localinfo_past_events_value_error']):
#     # with pytest.raises(ValidationError):
#     with pytest.raises(TypeError):
#         # localinfo
#         LocalInfo(**localinfo)

# ---------------------------------------------------------------------------
# Test helpers & fixtures
# ---------------------------------------------------------------------------

def fake_local_info_service():
    """Fake que satisfaz o contrato `AbstractLocalInfoService`."""
    
    class FakeLocalInfo:
        # precisa ser assíncrono porque o endpoint faz `await`
        async def get_by_name(self, location_name: str):
            return None  # ou qualquer comportamento desejado
        
    return FakeLocalInfo()

@pytest.mark.anyio
async def test_endpoint_dependency_override(client: TestClient, auth_header: dict[str, str]):
    app.dependency_overrides[provide_local_info_service] = fake_local_info_service
    # agora qualquer chamada à rota vai usar esse fake em vez do padrão
    resp = client.get(EVENTS_LOCAL_INFO_BY_NAME_ROUTE("fake"), headers=auth_header)
    assert resp.status_code == 404
    app.dependency_overrides = {}  # Limpe sempre após!