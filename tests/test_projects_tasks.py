from tests.conftest import register_user, login_user, auth_headers


def test_project_crud_owner_access(client):
    register_user(client, "u1@test.com", "secret123")
    tokens = login_user(client, "u1@test.com", "secret123").json()
    h = auth_headers(tokens["access_token"])

    # create project
    r = client.post("/projects", json={"title": "Sem7", "description": "Labs"}, headers=h)
    assert r.status_code == 201
    project = r.json()
    pid = project["id"]

    # list projects
    r = client.get("/projects", headers=h)
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()]
    assert pid in ids

    # update project
    r = client.patch(f"/projects/{pid}", json={"title": "Sem7 Updated"}, headers=h)
    assert r.status_code == 200
    assert r.json()["title"] == "Sem7 Updated"

    # delete project
    r = client.delete(f"/projects/{pid}", headers=h)
    assert r.status_code == 204


def test_project_forbidden_for_other_user(client):
    # user1
    register_user(client, "u1@test.com", "secret123")
    t1 = login_user(client, "u1@test.com", "secret123").json()
    h1 = auth_headers(t1["access_token"])

    # user2
    register_user(client, "u2@test.com", "secret123")
    t2 = login_user(client, "u2@test.com", "secret123").json()
    h2 = auth_headers(t2["access_token"])

    # user1 creates project
    p = client.post("/projects", json={"title": "Private", "description": None}, headers=h1).json()
    pid = p["id"]

    # user2 can't read it
    r = client.get(f"/projects/{pid}", headers=h2)
    assert r.status_code == 403


def test_tasks_flow(client):
    register_user(client, "u1@test.com", "secret123")
    tokens = login_user(client, "u1@test.com", "secret123").json()
    h = auth_headers(tokens["access_token"])

    # create project
    p = client.post("/projects", json={"title": "Proj", "description": ""}, headers=h).json()
    pid = p["id"]

    # create task
    r = client.post(
        f"/projects/{pid}/tasks",
        json={"title": "Task1", "description": "Do it", "priority": 4, "due_date": None},
        headers=h,
    )
    assert r.status_code == 201
    task = r.json()
    tid = task["id"]
    assert task["status"] == "todo"

    # list tasks
    r = client.get(f"/projects/{pid}/tasks", headers=h)
    assert r.status_code == 200
    assert len(r.json()) == 1

    # update task status
    r = client.patch(f"/tasks/{tid}", json={"status": "done"}, headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "done"

    # delete task
    r = client.delete(f"/tasks/{tid}", headers=h)
    assert r.status_code == 204
