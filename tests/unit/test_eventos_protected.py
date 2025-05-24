def test_eventos_requires_auth(client):
    r = client.get("/api/v1/eventos")
    assert r.status_code == 401          # sem token → não autorizado

def test_eventos_with_auth(client, auth_header):
    r = client.get("/api/v1/eventos", headers=auth_header)
    assert r.status_code == 200          # com token → sucesso
