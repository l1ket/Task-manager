import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-with-32-plus-bytes")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
os.environ.setdefault("POSTGRES_DB", "task_manager_test")
os.environ.setdefault("PORTS", "5432")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
