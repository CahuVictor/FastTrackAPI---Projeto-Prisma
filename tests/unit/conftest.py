
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

# @pytest.fixture
# def evento_valido():
#     return {
#         "title": "Concerto de Jazz",
#         "description": "Uma apresentação musical.",
#         "event_date": "2025-06-01T20:00:00",
#         "participants": ["Alice", "Bruno"],
#         "local_info": {
#             "location_name": "Auditório Central",
#             "capacity": 200,
#             "venue_type": "Auditorio",
#             "is_accessible": True,
#             "address": "Rua Exemplo, 123",
#             "past_events": ["Feira 2023", "Hackathon"]
#         }
#     }

# @pytest.fixture
# def evento_invalido():
#     return {
#         "title": "Evento Incompleto",
#         "event_date": "2025-06-01T20:00:00",
#         "participants": ["Zé"]
#     }

@pytest.fixture
def evento(request):
    if request.param == "evento_valido":
        return {
            "title": "Concerto de Jazz",
            "description": "Uma apresentação musical.",
            "event_date": "2025-06-01T20:00:00",
            "participants": ["Alice", "Bruno"],
            "local_info": {
                "location_name": "Auditório Central",
                "capacity": 200,
                "venue_type": "Auditorio",
                "is_accessible": True,
                "address": "Rua Exemplo, 123",
                "past_events": ["Feira 2023", "Hackathon"]
            }
        }
    elif request.param == "evento_valido_com_id":
        return {
            "id": 1,
            "title": "Concerto de Jazz",
            "description": "Uma apresentação musical.",
            "event_date": "2025-06-01T20:00:00",
            "participants": ["Alice", "Bruno"],
            "local_info": {
                "location_name": "Auditório Central",
                "capacity": 200,
                "venue_type": "Auditorio",
                "is_accessible": True,
                "address": "Rua Exemplo, 123",
                "past_events": ["Feira 2023", "Hackathon"]
            }
        }
    elif request.param == "evento_invalido":
        return {
            "title": "Incompleto",
            "event_date": "2025-06-01T20:00:00",
            "participants": ["Zé"]
        }
    else:
        raise ValueError(f"Fixture de evento desconhecida: {request.param}")