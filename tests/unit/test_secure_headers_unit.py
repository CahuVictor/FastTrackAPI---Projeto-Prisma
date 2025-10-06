# tests/unit/test_secure_headers_unit.py

from fastapi import FastAPI
from starlette.testclient import TestClient

from app.middleware.secure_headers import SecureHeadersMiddleware

def test_secure_headers_applied():
    # Instância mínima da FastAPI
    app = FastAPI()

    # Rota de teste
    @app.get("/teste-seguro")
    def exemplo():
        return {"msg": "ok"}

    # Aplica o middleware manualmente
    app.add_middleware(SecureHeadersMiddleware)

    # Cria o cliente de teste
    client = TestClient(app)

    # Realiza uma requisição
    response = client.get("/teste-seguro")

    # Verificações
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Strict-Transport-Security") == "max-age=63072000; includeSubDomains; preload"
    assert headers.get("Referrer-Policy") == "no-referrer"
    assert headers.get("Permissions-Policy") == "geolocation=(), microphone=(), camera=()"
