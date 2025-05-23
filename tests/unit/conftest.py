
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