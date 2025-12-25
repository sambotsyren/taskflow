from tests.conftest import register_user, login_user, auth_headers


def test_admin_forbidden_for_user(client):
    register_user(client, "u1@test.com", "secret123")
    tokens = login_user(client, "u1@test.com", "secret123").json()

    r = client.get("/admin/users", headers=auth_headers(tokens["access_token"]))
    assert r.status_code == 403


def test_admin_can_list_users(client, admin_user):
    # логинимся админом (он создан фикстурой admin_user)
    tokens = login_user(client, "admin@test.com", "adminpass").json()
    h = auth_headers(tokens["access_token"])

    r = client.get("/admin/users", headers=h)
    assert r.status_code == 200
    users = r.json()
    assert any(u["email"] == "admin@test.com" for u in users)


def test_admin_can_block_user(client, admin_user):
    # создаём обычного пользователя
    r = register_user(client, "victim@test.com", "secret123")
    victim_id = r.json()["id"]

    # логин админа
    tokens = login_user(client, "admin@test.com", "adminpass").json()
    h = auth_headers(tokens["access_token"])

    # блокируем
    r = client.patch(f"/admin/users/{victim_id}", json={"is_active": False}, headers=h)
    assert r.status_code == 200
    assert r.json()["is_active"] is False

    # теперь victim не может залогиниться
    r = login_user(client, "victim@test.com", "secret123")
    assert r.status_code == 401
