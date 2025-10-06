# app/services/mock_local_info.py
import unicodedata
from structlog import get_logger

from app.schemas.local_info import LocalInfoResponse
from app.services.interfaces.local_info_protocol import AbstractLocalInfoService

from app.schemas.venue_type import VenueTypes

logger = get_logger().bind(module="mock_local_info")

class MockLocalInfoService(AbstractLocalInfoService):
    def __init__(self):
        self._db = [  # já tem essa lista de mocks
            LocalInfoResponse(location_name="cesar", capacity=200, venue_type=VenueTypes.AUDITORIO, is_accessible=True, address="Rua Bione, 220", manually_edited=False),
            LocalInfoResponse(location_name="auditorio central", capacity=350, venue_type=VenueTypes.AUDITORIO, is_accessible=True, address="Av. Central, 123", manually_edited=False),
            LocalInfoResponse(location_name="salao azul", capacity=100, venue_type=VenueTypes.SALAO, is_accessible=False, address="Rua Azul, 10", manually_edited=False),
            LocalInfoResponse(location_name="teatro municipal", capacity=500, venue_type=VenueTypes.AUDITORIO, is_accessible=True, address="Praça Matriz, 5", manually_edited=False),
            LocalInfoResponse(location_name="espaço verde", capacity=150, venue_type=VenueTypes.SALAO, is_accessible=False, address="Rua das Palmeiras, 200", manually_edited=False),
            LocalInfoResponse(location_name="galpão criativo", capacity=80, venue_type=VenueTypes.SALAO, is_accessible=True, address="Rua do Comércio, 45", manually_edited=False),
            LocalInfoResponse(location_name="centro cultural", capacity=400, venue_type=VenueTypes.AUDITORIO, is_accessible=True, address="Av. Cultura, 555", manually_edited=False),
            LocalInfoResponse(location_name="biblioteca", capacity=60, venue_type=VenueTypes.SALAO, is_accessible=True, address="Rua do Saber, 77", manually_edited=False),
            LocalInfoResponse(location_name="sala amarela", capacity=40, venue_type=VenueTypes.SALAO, is_accessible=False, address="Rua Sol, 33", manually_edited=False),
            LocalInfoResponse(location_name="auditorio beta", capacity=220, venue_type=VenueTypes.AUDITORIO, is_accessible=True, address="Av. Beta, 101", manually_edited=False),
        ]

    def _normalize(self, text: str) -> str:
        """Remove acentos, _/–, espaços duplicados e coloca tudo em minúsculas."""
        original = text
        
        text = text.strip().lower()
        text = text.replace("_", " ").replace("-", " ")

        # remove acentos
        text = unicodedata.normalize("NFD", text)
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")

        # colapsa espaços múltiplos
        normalized = " ".join(text.split())
        
        logger.debug("Nome normalizado", original=original, normalizado=normalized)
        return normalized

    # era: async def get_by_name(…)
    async def get_by_name(self, location_name: str) -> LocalInfoResponse | None:
        name = self._normalize(location_name)
        for item in self._db:
            if item.location_name == name:
                logger.info("Local encontrado", original=location_name, normalizado=name)
                return item

        logger.warning("Local não encontrado", original=location_name, normalizado=name)
        return None