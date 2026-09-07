from fastapi.testclient import TestClient

from whisper_street.api.app import create_app
from whisper_street.core.types import default_capabilities


def _client() -> TestClient:
    return TestClient(create_app())


def test_capabilities_matches_default() -> None:
    response = _client().get("/v1/capabilities")
    assert response.status_code == 200

    caps = default_capabilities()
    assert response.json() == {
        "models": list(caps.models),
        "languages": list(caps.languages),
        "output_formats": list(caps.output_formats),
        "max_file_size_bytes": caps.max_file_size_bytes,
        "max_audio_duration_seconds": caps.max_audio_duration_seconds,
        "max_concurrent_jobs_per_caller": caps.max_concurrent_jobs_per_caller,
        "request_rate_limit_per_minute": caps.request_rate_limit_per_minute,
        "result_retention_seconds": caps.result_retention_seconds,
        "url_fetch_enabled": caps.url_fetch_enabled,
    }


def test_capabilities_models_and_languages_are_empty() -> None:
    response = _client().get("/v1/capabilities")
    body = response.json()
    assert body["models"] == []
    assert body["languages"] == []
