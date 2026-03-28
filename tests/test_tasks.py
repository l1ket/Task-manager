from datetime import datetime, timezone
from types import SimpleNamespace

from app.api.v1 import routes_tasks
from app.api.v1.util.utils import create_access_token


def _task(task_id, email="user@example.com", title="Task", description=None, status="NEW"):
    return SimpleNamespace(
        id=task_id,
        email=email,
        title=title,
        description=description,
        status=status,
        created_at=datetime.now(timezone.utc),
    )


def _auth_headers():
    token, _ = create_access_token("user@example.com")
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_tasks(client, monkeypatch):
    tasks = []

    async def fake_create_task(session, email, payload):
        task = _task(
            task_id=len(tasks) + 1,
            email=email,
            title=payload.title,
            description=payload.description,
        )
        tasks.append(task)
        return task

    async def fake_list_tasks(session, email):
        return [task for task in tasks if task.email == email]

    monkeypatch.setattr(routes_tasks.db, "create_task", fake_create_task)
    monkeypatch.setattr(routes_tasks.db, "list_tasks", fake_list_tasks)

    create_response = client.post(
        "/tasks",
        json={"title": "First task", "description": "Details"},
        headers=_auth_headers(),
    )
    list_response = client.get("/tasks", headers=_auth_headers())

    assert create_response.status_code == 201
    assert create_response.json()["title"] == "First task"
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["title"] == "First task"


def test_get_single_task_for_owner(client, monkeypatch):
    async def fake_get_task_for_user(session, email, task_id):
        return _task(task_id=task_id, email=email, title="Owned task")

    monkeypatch.setattr(routes_tasks.db, "get_task_for_user", fake_get_task_for_user)

    response = client.get("/tasks/5", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json()["id"] == 5
    assert response.json()["title"] == "Owned task"


def test_task_not_found_for_other_user(client, monkeypatch):
    async def fake_get_task_for_user(session, email, task_id):
        return None

    monkeypatch.setattr(routes_tasks.db, "get_task_for_user", fake_get_task_for_user)

    response = client.get("/tasks/999", headers=_auth_headers())

    assert response.status_code == 404
    assert response.json()["detail"] == "Задача не найдена."


def test_update_task(client, monkeypatch):
    task = _task(task_id=3, title="Old", description="Before", status="NEW")

    async def fake_get_task_for_user(session, email, task_id):
        return task

    async def fake_update_task(session, task, payload):
        task.title = payload.title or task.title
        task.description = payload.description
        task.status = payload.status or task.status
        return task

    monkeypatch.setattr(routes_tasks.db, "get_task_for_user", fake_get_task_for_user)
    monkeypatch.setattr(routes_tasks.db, "update_task", fake_update_task)

    response = client.put(
        "/tasks/3",
        json={"title": "Updated", "status": "DONE", "description": "After"},
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["status"] == "DONE"


def test_delete_task(client, monkeypatch):
    deleted = {"value": False}
    task = _task(task_id=4)

    async def fake_get_task_for_user(session, email, task_id):
        return task

    async def fake_delete_task(session, task):
        deleted["value"] = True

    monkeypatch.setattr(routes_tasks.db, "get_task_for_user", fake_get_task_for_user)
    monkeypatch.setattr(routes_tasks.db, "delete_task", fake_delete_task)

    response = client.delete("/tasks/4", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json()["message"] == "Задача удалена."
    assert deleted["value"] is True


def test_update_requires_payload(client, monkeypatch):
    async def fake_get_task_for_user(session, email, task_id):
        return _task(task_id=task_id)

    monkeypatch.setattr(routes_tasks.db, "get_task_for_user", fake_get_task_for_user)

    response = client.put("/tasks/1", json={}, headers=_auth_headers())

    assert response.status_code == 400
    assert response.json()["detail"] == "Нужно передать хотя бы одно поле для обновления."
