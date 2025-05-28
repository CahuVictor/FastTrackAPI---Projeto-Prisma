# app/services/interfaces/local_info.py
from typing import Protocol
from app.schemas.local_info import LocalInfo

class AbstractLocalInfoService(Protocol):
    def get_by_name(self, location_name: str) -> LocalInfo | None: ...