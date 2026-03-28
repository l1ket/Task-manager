from types import SimpleNamespace

from app.api.v1 import routes_auth
from app.api.v1.util import utils


def test_register_success(client, monkeypatch):
    created = {}

    async def fake_get_user_by_email(session, email):
        return None

    async def fake_create_user(session, email, password_hash):
        created["email"] = email
        created["password_hash"] = password_hash
        return SimpleNamespace(email=email, password_hash=password_hash)

    monkeypatch.setattr(routes_auth.db, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(routes_auth.db, "create_user", fake_create_user)

    response = client.post(
        "/auth/register",
        json={"email": "danilizmestev124@gmail.com", "password": "StrongPass1!"},
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Пользователь успешно зарегистрирован."
    assert created["email"] == "danilizmestev124@gmail.com"
    assert created["password_hash"] != "StrongPass1!"


def test_register_duplicate_email(client, monkeypatch):
    async def fake_get_user_by_email(session, email):
        return SimpleNamespace(email=email)

    monkeypatch.setattr(routes_auth.db, "get_user_by_email", fake_get_user_by_email)

    response = client.post(
        "/auth/register",
        json={"email": "danilizmestev124@gmail.com", "password": "StrongPass1!"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Пользователь с таким email уже существует."


def test_login_success(client, monkeypatch):
    hashed_password = utils.hash_password("StrongPass1!")

    async def fake_get_user_by_email(session, email):
        return SimpleNamespace(email=email, password_hash=hashed_password)

    monkeypatch.setattr(routes_auth.db, "get_user_by_email", fake_get_user_by_email)

    response = client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "StrongPass1!"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_at"]


def test_login_invalid_password(client, monkeypatch):
    hashed_password = utils.hash_password("StrongPass1!")

    async def fake_get_user_by_email(session, email):
        return SimpleNamespace(email=email, password_hash=hashed_password)

    monkeypatch.setattr(routes_auth.db, "get_user_by_email", fake_get_user_by_email)

    response = client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "WrongPass1!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный email или пароль."


def test_invalid_token_returns_401(client):
    response = client.get(
        "/tasks",
        headers={"Authorization": "Bearer definitely.invalid.token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Не удалось проверить учетные данные."
