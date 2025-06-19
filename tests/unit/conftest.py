# tests/unit/conftest.py -> Verificar se pode ficar na raiz de tests/
import pytest
from datetime import datetime
# from fastapi import HTTPException
from fastapi.testclient import TestClient
import fakeredis
import asyncio

# from app.main import app
from app.main import app as fastapi_app   # FastAPI já criado em app.main

# from app.schemas.local_info import LocalInfo
from app.services.mock_local_info import MockLocalInfoService

from app.repositories.evento_mem import InMemoryEventRepo
from app.deps import provide_event_repo

from app.deps import provide_redis

# ------------------------------------------------------------------------------
# --------------------------- XXXX --------------------------
# ------------------------------------------------------------------------------


@pytest.fixture(scope="session")
def app():
    """Instância única da aplicação para todos os testes."""
    return fastapi_app

@pytest.fixture(scope="session")
# def client():
def client(app) -> TestClient:
    """Client “cru”, sem header de autorização."""
    with TestClient(app) as c:
        yield c
        
# ------------------------------------------------------------------------------
# --------------------------- CLIENTES / AUTENTICAÇÃO --------------------------
# ------------------------------------------------------------------------------

@pytest.fixture
def login_data():
    return {
        "username": "alice",
        "password": "secret123"
    }

@pytest.fixture
def access_token(client: TestClient, login_data):
    resp = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]

@pytest.fixture
def auth_header(access_token):
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def client_autenticado(access_token):
    """Retorna um TestClient que envia o header Authorization automaticamente."""
    class _AuthClient(TestClient):                              # noqa: D401
        def request(self, method, url, **kwargs):
            headers = kwargs.pop("headers", {}) or {}
            headers["Authorization"] = f"Bearer {access_token}"
            return super().request(method, url, headers=headers, **kwargs)
    with _AuthClient(app) as c:
        yield c

# ------------------------------------------------------------------------------
# --------------------------------- FIXTURES -----------------------------------
# ------------------------------------------------------------------------------

# ---------- Eventos -----------------------------------------------------------

@pytest.fixture
def event(request):
    if request.param == "evento_valido":
        return {
            "title": "Concerto de Jazz",
            "description": "Uma apresentação musical.",
            "event_date": "2025-06-01T20:00:00",
            "participants": ["Alice", "Bruno"],
            "city": "Recife",
            "local_info": {
                "location_name": "auditório central",  # minúsculo!
                "capacity": 200,
                "venue_type": "Auditorio",
                "is_accessible": True,
                "address": "Rua Exemplo, 123",
                "past_events": ["Feira 2023", "Hackathon"],
                "manually_edited": False
            }
        }
    elif request.param == "evento_valido_com_id":
        return {
            "id": 1,
            "title": "Concerto de Jazz",
            "description": "Uma apresentação musical.",
            "event_date": "2025-06-01T20:00:00",
            "participants": ["Alice", "Bruno"],
            "city": "fortaleza",
            "local_info": {
                "location_name": "Auditório Central",
                "capacity": 200,
                "venue_type": "Auditorio",
                "is_accessible": True,
                "address": "Rua Exemplo, 123",
                "past_events": ["Feira 2023", "Hackathon"],
                "manually_edited": False
            }
        }
    elif request.param == "evento_valido_com_id_e_forecast":
        return {
            "id": 123,  # pode ser qualquer valor (a rota sobrescreve)
            "title": "Concerto de Jazz",
            "description": "Uma apresentação musical.",
            "event_date": "2025-06-01T20:00:00",
            "city": "Recife",
            "participants": ["Alice", "Bruno"],
            "local_info": {
                "location_name": "auditório central",
                "capacity": 200,
                "venue_type": "Auditorio",
                "is_accessible": True,
                "address": "Rua Exemplo, 123",
                "past_events": ["Feira 2023", "Hackathon"],
                "manually_edited": False
            },
            "forecast_info": {
                "forecast_datetime": "2025-06-01T18:00:00",  # pode usar a data do evento
                "temperature": 28.0,
                "weather_main": "Clear",
                "weather_desc": "Céu limpo",
                "humidity": 60,
                "wind_speed": 3.0
            }
        }
    elif request.param == "eventos_validos_lote":
        return [
            {
                "title": "Evento 1",
                "description": "Primeiro evento.",
                "event_date": "2025-06-01T20:00:00",
                "city": "Recife",
                "participants": ["Alice", "Bruno"],
                "local_info": {
                    "location_name": "auditório central",
                    "capacity": 100,
                    "venue_type": "Auditorio",
                    "is_accessible": True,
                    "address": "Rua Principal, 1",
                    "past_events": ["Feira 2023"],
                    "manually_edited": False
                }
            },
            {
                "title": "Evento 2",
                "description": "Segundo evento.",
                "event_date": "2025-07-10T19:00:00",
                "city": "Olinda",
                "participants": ["Carlos", "Diana"],
                "local_info": {
                    "location_name": "sala multiuso",
                    "capacity": 50,
                    "venue_type": "Salao",
                    "is_accessible": False,
                    "address": "Rua Secundária, 2",
                    "past_events": [],
                    "manually_edited": False
                }
            }
        ]
    elif request.param == "evento_invalido":
        return {
            "title": "Incompleto",
            "event_date": "2025-06-01T20:00:00",
            "participants": ["Zé"]
        }
    else:
        raise ValueError(f"Fixture de evento desconhecida: {request.param}")

# ---------- Local Info --------------------------------------------------------

@pytest.fixture
def localinfo(request):
    if request.param == "localinfo_valido":
        return {
            "location_name": "auditório central",
            "capacity": 10,
            "venue_type": "Auditorio",
            "is_accessible": True,
            "address": "Rua X, 1",
            "past_events": ["Evento 2021"],
            "manually_edited": False
        }
    elif request.param == "localinfo_type_error":
        return {
            "location_name": 123,  # Não string
            "capacity": 10,
            "venue_type": "Auditorio",
            "is_accessible": True,
            "address": "Rua X, 1",
            "past_events": ["Evento 2021"],
            "manually_edited": False
        }
    elif request.param == "localinfo_past_events_type_error":
        return {
            "location_name": "local",
            "capacity": 10,
            "venue_type": "Auditorio",
            "is_accessible": True,
            "address": "Rua X, 1",
            "past_events": "não é lista",  # Deve ser lista
            "manually_edited": False
        }
    elif request.param == "localinfo_past_events_value_error":
        return {
            "location_name": "local",
            "capacity": 10,
            "venue_type": "Auditorio",
            "is_accessible": True,
            "address": "Rua X, 1",
            "past_events": [123],  # Deve ser lista de strings
            "manually_edited": False
        }
    else:
        raise ValueError(f"Fixture de evento desconhecida: {request.param}")

# Unit helper – serviço fake em memória
@pytest.fixture
def mock_local_info_service():
    return MockLocalInfoService()

# ---------- Datas auxiliares --------------------------------------------------

@pytest.fixture
def data_agora_iso():
    return datetime.now().isoformat()

@pytest.fixture
def dt_now_iso() -> str:
    """ISO agora – para forecast_info."""
    return datetime.now().isoformat()

# ---------- Repositories --------------------------------------------------

@pytest.fixture
def repo(app):
    """Mesmo repositório usado pelo app; útil para asserts diretos."""
    return next(iter(app.dependency_overrides.values()))()  # _shared_repo já registra

@pytest.fixture(autouse=True)
def _shared_repo(app):
    repo = InMemoryEventRepo()
    app.dependency_overrides[provide_event_repo] = lambda: repo
    yield
    repo.delete_all()       # reseta entre testes
    
# ---------- Redis --------------------------------------------------

@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    r = fakeredis.FakeRedis(decode_responses=True)
    # monkeypatch.setitem(app.main.app.dependency_overrides, provide_redis, lambda: r)
    monkeypatch.setitem(
        fastapi_app.dependency_overrides,     # usa a instância correta
        provide_redis,
        lambda: r
    )
    yield r

@pytest.fixture(autouse=True)
def patch_create_task(monkeypatch):
    """
    Substitui `asyncio.create_task` por uma versão segura para
    handlers síncronos executados dentro do ThreadPool do FastAPI.

    ── Como funciona ──────────────────────────────────────────────
    • Se já existe um event-loop ativo, delega normalmente.
    • Caso contrário (thread do ThreadPool), cria um loop local,
      roda o coroutine até o fim e devolve um DummyTask.
    """

    def _safe_create_task(coro, *args, **kwargs):             # noqa: D401
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(coro, *args, **kwargs)
        except RuntimeError:
            # estamos numa thread sem loop – roda o coroutine “inline”
            _loop = asyncio.new_event_loop()
            try:
                _loop.run_until_complete(coro)
            finally:
                _loop.close()

            class _DummyTask:          # objeto mínimo para quem, porventura,
                def cancel(self):      # tente chamar .cancel() no retorno
                    pass
            return _DummyTask()

    # monkeypatch.patch("asyncio.create_task", _safe_create_task)
    # substitui a função no próprio módulo asyncio
    monkeypatch.setattr(asyncio, "create_task", _safe_create_task, raising=True)
    yield