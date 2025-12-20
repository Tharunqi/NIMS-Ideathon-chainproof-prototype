from fastapi.testclient import TestClient
from app.main import app


def test_health_ok():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200


def test_breaker_state_endpoint():
    client = TestClient(app)
    r = client.get("/state/breaker")
    assert r.status_code == 200
    assert "state" in r.json()
