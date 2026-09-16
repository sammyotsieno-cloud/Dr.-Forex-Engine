"""Tests for the application health endpoint."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    """The health endpoint should report that the service is operational."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "dr-forex-engine",
        "version": "0.1.0",
    }
