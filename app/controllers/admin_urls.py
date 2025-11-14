# app\api\v1\endpoints\admin_urls.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from pathlib import Path
import json

router = APIRouter(prefix="/admin", tags=["Admin"])

class URLUpdateRequest(BaseModel):
    service: str  # "forecast_info_url" ou "local_info_url"
    url: HttpUrl

ALLOWED_KEYS = {"forecast_info_url", "local_info_url"}
RUNTIME_PATH = Path("runtime_urls.json")


@router.put("/update-service-url", status_code=204)
def update_service_url(payload: URLUpdateRequest):
    if payload.service not in ALLOWED_KEYS:
        raise HTTPException(status_code=400, detail="Serviço não permitido")

    # Lê o conteúdo atual
    urls = {}
    if RUNTIME_PATH.exists():
        try:
            with RUNTIME_PATH.open("r", encoding="utf-8") as f:
                urls = json.load(f)
        except Exception:
            pass

    # Atualiza e salva
    urls[payload.service] = str(payload.url)
    with RUNTIME_PATH.open("w", encoding="utf-8") as f:
        json.dump(urls, f, indent=2, ensure_ascii=False)

    return
