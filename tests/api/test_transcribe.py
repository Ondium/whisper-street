from fastapi.testclient import TestClient

from whisper_street.api.app import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_transcribe_returns_pipeline_not_implemented() -> None:
    response = _client().post(
        "/v1/transcribe", json={"source_url": "https://example.com/audio.wav"}
    )
    assert response.status_code == 501
    body = response.json()
    assert body["error"]["code"] == "PIPELINE_NOT_IMPLEMENTED"
    assert body["error"]["retryable"] is False


def test_transcribe_requires_audio_or_source_url() -> None:
    response = _client().post("/v1/transcribe", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["field"] == "audio"
