# tests/unit/test_eventos_completo copy.py
import pytest
from app.services.mock_local_info import MockLocalInfoService

def get_token(client_autenticado):
    resp = client_autenticado.post("/api/v1/auth/login", data={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_busca_local_info(client_autenticado):
    # Testa usando o serviço via endpoint autenticado
    resp = client_autenticado.get("/api/v1/local_info?location_name=auditório central")
    assert resp.status_code == 200
    assert "location_name" in resp.json()

def test_servico_mock_local_info_unitario():
    # Testa o serviço diretamente, sem endpoint
    service = MockLocalInfoService()
    info = service.get_by_name("auditório central")
    assert info is not None
    info_none = service.get_by_name("local inexistente 999")
    assert info_none is None
