# tests/unit/test_localinfo.py

import pytest

from app.schemas.local_info import LocalInfo
from app.services.mock_local_info import MockLocalInfoService

def test_location_name_validator_typeerror():
    with pytest.raises(TypeError):
        LocalInfo(
            location_name=123,  # Não string
            capacity=10,
            venue_type="Auditorio",
            is_accessible=True,
            address="Rua X, 1",
            past_events=[],
            manually_edited=False
        )

def test_past_events_validator_typeerror():
    with pytest.raises(TypeError):
        LocalInfo(
            location_name="local",
            capacity=10,
            venue_type="Auditorio",
            is_accessible=True,
            address="Rua X, 1",
            past_events="não é lista",  # Deve ser lista
            manually_edited=False
        )

def test_past_events_validator_valueerror():
    with pytest.raises(ValueError):
        LocalInfo(
            location_name="local",
            capacity=10,
            venue_type="Auditorio",
            is_accessible=True,
            address="Rua X, 1",
            past_events=[123],  # Deve ser lista de strings
            manually_edited=False
        )

def test_get_local_info_by_name_none():
    service = MockLocalInfoService()
    assert service.get_by_name("não existe") is None

def test_mock_local_info_service():
    service = MockLocalInfoService()
    info = service.get_by_name("auditorio central")
    assert info is not None