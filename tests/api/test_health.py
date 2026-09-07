from fastapi.testclient import TestClient

from whisper_street.api.app import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_health_ok() -> None:
    response = _client().get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "live": True,
        "ready": True,
        "version": "0.1.0",
    }
