# app\services\local_info_api.py
import httpx
from app.services.interfaces.local_info_protocol import AbstractLocalInfoService
from app.schemas.local_info import LocalInfo
from app.utils.service_url import get_service_url

class LocalInfoService(AbstractLocalInfoService):
    """
    Implementação real que consulta a API externa de LocalInfo.
    """

    async def get_info_by_coordinates(self, lat: float, lon: float) -> LocalInfo:
        base_url = get_service_url("local_info_url")
        url = f"{base_url}/local_info?lat={lat}&lon={lon}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

        return LocalInfo(**data)
