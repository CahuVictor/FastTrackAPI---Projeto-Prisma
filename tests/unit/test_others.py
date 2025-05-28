# tests/unit/test_others.py
import pytest

from app.main import app
from app.deps import provide_local_info_service

from tests.unit.conftest import get_token

@pytest.fixture
def token(client):
    resp = client.post("/api/v1/auth/login", data={"username": "alice", "password": "secret123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def fake_local_info_service():
    class FakeLocalInfo:
        def get_by_name(self, location_name):
            return None  # ou qualquer comportamento desejado
    return FakeLocalInfo()

def test_endpoint_com_dependencia_override(client, token):
    app.dependency_overrides[provide_local_info_service] = fake_local_info_service
    # agora qualquer chamada à rota vai usar esse fake em vez do padrão
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/v1/local_info?location_name=fake", headers=headers)
    assert resp.status_code == 404
    app.dependency_overrides = {}  # Limpe sempre após!
