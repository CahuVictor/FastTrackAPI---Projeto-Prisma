# tests/unit/test_rate_limiter.py

from fastapi import FastAPI, Request
from starlette.testclient import TestClient
from app.middleware.rate_limiter import setup_rate_limiter, limiter

def test_rate_limiter_blocks_after_limit():
    app = FastAPI()

    @app.get("/ping")
    @limiter.limit("3/minute")
    async def ping(request: Request):  # ✅ necessário para funcionar
        return {"msg": "pong"}

    setup_rate_limiter(app)
    client = TestClient(app)

    # Faz 3 requisições válidas
    for _ in range(3):
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json() == {"msg": "pong"}

    # A quarta deve ser bloqueada
    response = client.get("/ping")
    assert response.status_code == 429
    assert response.json()["detail"] == "3 per 1 minute"
