# test_auth.py
def test_login_success(client_autenticado):
    r = client_autenticado.post(
        "/api/v1/auth/login",
        data={"username": "alice", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body

def test_rotas_protegidas_sem_token(client):
    resp = client.get("/api/v1/eventos")
    assert resp.status_code == 401
    assert resp.json()["detail"] in {"Not authenticated", "Credenciais inválidas"}

def get_token(client_autenticado):
    resp = client_autenticado.post("/api/v1/auth/login", data={
        "username": "alice",
        "password": "secret123"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]