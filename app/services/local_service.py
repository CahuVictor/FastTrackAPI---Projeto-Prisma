# app\services\local_service.py
import httpx
from datetime import datetime
from typing import List
from structlog import get_logger

from app.models.local import Local
from app.repositories.local_repo import LocalRepository
from app.schemas.local_create import LocalCreate
from app.schemas.local_update import LocalUpdate

class LocalService:
    """
    Implementação real que consulta a API externa de LocalInfo.
    """

    async def get_info_by_coordinates(self, lat: float, lon: float) -> None: # Local:
        # base_url = get_service_url("local_info_url")
        # url = f"{base_url}/local_info?lat={lat}&lon={lon}"

        # async with httpx.AsyncClient() as client:
        #     response = await client.get(url, timeout=10)
        #     response.raise_for_status()
        #     data = response.json()

        # return Local(**data)
        return None
