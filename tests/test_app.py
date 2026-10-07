
import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "OK"
    assert data["service"] == "secure-flask-microservice"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"


def test_readiness_without_database(client, monkeypatch):
    monkeypatch.setenv("DB_HOST", "127.0.0.1")

    response = client.get("/ready")

    assert response.status_code == 503

    data = response.get_json()

    assert data["status"] == "not_ready"


def test_data_without_database(client, monkeypatch):
    monkeypatch.setenv("DB_HOST", "127.0.0.1")

    response = client.get("/data")

    assert response.status_code == 503

    data = response.get_json()

    assert data["status"] == "error"


def test_users_without_database(client, monkeypatch):
    monkeypatch.setenv("DB_HOST", "127.0.0.1")

    response = client.get("/users")

    assert response.status_code == 503

    data = response.get_json()

    assert data["status"] == "error"
