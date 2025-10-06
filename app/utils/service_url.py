# app\utils\service_url.py
import json
from pathlib import Path
from app.core.config import get_settings

RUNTIME_PATH = Path("runtime_urls.json")
settings = get_settings()

def get_service_url(service: str) -> str:
    """
    Retorna a URL do serviço, priorizando override em runtime_urls.json.
    """
    if RUNTIME_PATH.exists():
        try:
            with RUNTIME_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if service in data:
                    return data[service]
        except Exception as e:
            print(f"[WARN] Falha ao ler runtime_urls.json: {e}")

    return {
        "local_info_url": settings.local_info_url,
        "forecast_info_url": settings.forecast_info_url
    }.get(service, "")
