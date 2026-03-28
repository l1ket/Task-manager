# Task Manager API

Небольшой backend-сервис на FastAPI для регистрации пользователей и управления задачами.

## Стек

- FastAPI
- PostgreSQL
- SQLAlchemy Async
- Alembic
- Docker Compose
- Pytest

## Быстрый старт

1. Создай `.env` на основе `.env.example`.
2. Запусти сервисы:

```bash
docker compose up --build
```

3. После старта API будет доступен на `http://localhost:8000`.
4. Swagger UI будет доступен на `http://localhost:8000/docs`.

## Локальный запуск

```bash
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\alembic.exe upgrade head
venv\Scripts\uvicorn.exe app.main:app --reload
```

## Переменные окружения

- `SECRET_KEY` - секрет для JWT
- `POSTGRES_USER` - пользователь базы данных
- `POSTGRES_PASSWORD` - пароль базы данных
- `POSTGRES_DB` - имя базы данных
- `POSTGRES_HOST` - хост базы данных, по умолчанию `postgres`
- `PORTS` - порт PostgreSQL
- `ACCESS_TOKEN_EXPIRE_MINUTES` - срок жизни access token

## Основные маршруты

- `GET /` - healthcheck
- `POST /auth/register` - регистрация пользователя
- `POST /auth/login` - получение JWT токена
- `GET /tasks` - список задач текущего пользователя
- `POST /tasks` - создание задачи
- `GET /tasks/{task_id}` - получить одну задачу
- `PUT /tasks/{task_id}` - обновить задачу
- `DELETE /tasks/{task_id}` - удалить задачу

## Примеры запросов

Регистрация:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user@example.com\",\"password\":\"StrongPass1!\"}"
```

Логин:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=StrongPass1!"
```

Создание задачи:

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Купить молоко\",\"description\":\"После работы\"}"
```
