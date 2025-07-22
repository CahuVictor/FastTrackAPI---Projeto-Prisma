# tests/middleware/test_secure_headers.py
import pytest
import httpx
from starlette.status import HTTP_200_OK
from httpx import ASGITransport

from app.main import app

@pytest.mark.asyncio
async def test_secure_headers_are_present():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/docs")  # ou use uma rota sua como "/health"

    assert response.status_code == HTTP_200_OK

    headers = response.headers

    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Strict-Transport-Security") == "max-age=63072000; includeSubDomains; preload"
    assert headers.get("Referrer-Policy") == "no-referrer"
    assert headers.get("Permissions-Policy") == "geolocation=(), microphone=(), camera=()"
