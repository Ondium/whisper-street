from fastapi.testclient import TestClient

from whisper_street.api.app import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_unknown_job_returns_structured_404() -> None:
    response = _client().get("/v1/jobs/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "JOB_NOT_FOUND"
    assert body["error"]["field"] == "job_id"
    assert body["error"]["retryable"] is False
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]


def test_invalid_result_format_is_validation_error() -> None:
    response = _client().get("/v1/jobs/does-not-exist/result?format=xml")
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["field"] == "format"
    assert body["error"]["retryable"] is False
