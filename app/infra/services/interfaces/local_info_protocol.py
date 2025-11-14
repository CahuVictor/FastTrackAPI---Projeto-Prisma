# app/services/interfaces/local_info.py
from typing import Protocol
from app.schemas.local_create import LocalInfoResponse

class AbstractLocalInfoService(Protocol):
    async def get_by_name(self, location_name: str) -> LocalInfoResponse | None: ...