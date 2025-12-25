from tests.conftest import register_user, login_user, auth_headers


def test_register_and_login_and_me(client):
    r = register_user(client, "u1@test.com", "secret123")
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "u1@test.com"
    assert data["role"] == "user"

    r = login_user(client, "u1@test.com", "secret123")
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    r = client.get("/auth/me", headers=auth_headers(tokens["access_token"]))
    assert r.status_code == 200
    me = r.json()
    assert me["email"] == "u1@test.com"


def test_register_duplicate_email(client):
    r1 = register_user(client, "dup@test.com", "secret123")
    assert r1.status_code == 201

    r2 = register_user(client, "dup@test.com", "secret123")
    assert r2.status_code == 409


def test_login_wrong_password(client):
    register_user(client, "u2@test.com", "secret123")

    r = login_user(client, "u2@test.com", "wrongpass")
    assert r.status_code == 401


def test_refresh_token(client):
    register_user(client, "u3@test.com", "secret123")
    r = login_user(client, "u3@test.com", "secret123")
    tokens = r.json()

    # В твоём эндпоинте refresh_token — query parameter
    r = client.post("/auth/refresh", params={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    assert "access_token" in r.json()
