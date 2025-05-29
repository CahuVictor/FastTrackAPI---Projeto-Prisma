# tests/unit/test_auth.py
# (autenticação & autorização)

def test_login_success(client, login_data):
    r = client.post(
        "/api/v1/auth/login",
        data=login_data,
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

def test_eventos_requires_auth(client):
    r = client.get("/api/v1/eventos")
    assert r.status_code == 401          # sem token → não autorizado

def test_eventos_with_auth(client, auth_header):
    r = client.get("/api/v1/eventos", headers=auth_header)
    # pode ser 200 ou 404 (se não houver evento cadastrado ainda)
    assert r.status_code in (200, 404)          # com token → sucesso

# def test_acesso_autenticado(client, auth_header):
#     resp = client.get("/api/v1/eventos", headers=auth_header)
#     assert resp.status_code == 200