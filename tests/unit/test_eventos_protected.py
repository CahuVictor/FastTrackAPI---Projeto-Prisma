# tests/unit/test_eventos_protected.py

def test_eventos_requires_auth(client):
    r = client.get("/api/v1/eventos")
    assert r.status_code == 401          # sem token → não autorizado

def test_eventos_with_auth(client_autenticado, auth_header):
    r = client_autenticado.get("/api/v1/eventos", headers=auth_header)
    assert r.status_code == 200          # com token → sucesso
