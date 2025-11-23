# app/testing/factories/event_factory.py
from datetime import datetime, timezone
from typing import Any

from app.schemas.event.event_create import EventCreate

def make_dummy_event_create(**overrides: Any) -> EventCreate:
    """
    Factory para criar um EventCreate com dados padrão,
    permitindo sobrescrever qualquer campo.
    """
    base_data: dict[str, Any] = {
        "title": "Evento genérico",
        "description": "Descrição genérica",
        "event_date": datetime.now(tz=timezone.utc),
        "city": "Recife",
        "participants": [],
        "local_id": None,
        "forecast_id": None,
    }
    base_data.update(overrides)
    return EventCreate(**base_data)

# Nos testes, você usa:
# from app.testing.factories.event_factory import make_dummy_event_create

# def test_alguma_coisa():
#     payload = make_dummy_event_create(title="Título específico")
#     ...