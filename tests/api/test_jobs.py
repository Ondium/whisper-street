from fastapi.testclient import TestClient

from whisper_street.api.app import create_app
from whisper_street.api.deps import get_job_store
from whisper_street.core.types import (
    JobState,
    JobStatus,
    PipelineConfig,
    Segment,
    Transcript,
)


def _client() -> TestClient:
    return TestClient(create_app())


def test_create_job_is_queued() -> None:
    client = _client()
    response = client.post(
        "/v1/jobs", json={"source_url": "https://example.com/audio.wav"}
    )
    assert response.status_code == 202
    body = response.json()
    assert body["state"] == "queued"
    assert body["result"] is None
    job_id = body["job_id"]

    get_response = client.get(f"/v1/jobs/{job_id}")
    assert get_response.status_code == 200
    assert get_response.json()["job_id"] == job_id
    assert get_response.json()["state"] == "queued"


def test_create_job_accepts_opaque_audio_field() -> None:
    response = _client().post("/v1/jobs", json={"audio": "data:audio/wav;base64,AAAA"})
    assert response.status_code == 202
    assert response.json()["state"] == "queued"


def test_create_job_requires_audio_or_source_url() -> None:
    response = _client().post("/v1/jobs", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["field"] == "audio"


def test_create_job_rejects_unknown_output_format() -> None:
    response = _client().post(
        "/v1/jobs",
        json={"source_url": "https://example.com/a.wav", "output_formats": ["xml"]},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_unknown_job_is_404() -> None:
    response = _client().get("/v1/jobs/nope")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"


def test_result_on_queued_job_is_409_not_complete() -> None:
    client = _client()
    create = client.post("/v1/jobs", json={"source_url": "https://example.com/a.wav"})
    job_id = create.json()["job_id"]

    result = client.get(f"/v1/jobs/{job_id}/result")
    assert result.status_code == 409
    body = result.json()
    assert body["error"]["code"] == "JOB_NOT_COMPLETE"
    assert body["error"]["retryable"] is True


def test_cancel_job_then_result_is_409_cancelled() -> None:
    client = _client()
    create = client.post("/v1/jobs", json={"source_url": "https://example.com/a.wav"})
    job_id = create.json()["job_id"]

    cancel = client.delete(f"/v1/jobs/{job_id}")
    assert cancel.status_code == 200
    assert cancel.json()["state"] == "cancelled"

    get_after = client.get(f"/v1/jobs/{job_id}")
    assert get_after.json()["state"] == "cancelled"

    result = client.get(f"/v1/jobs/{job_id}/result")
    assert result.status_code == 409
    body = result.json()
    assert body["error"]["code"] == "JOB_CANCELLED"
    assert body["error"]["retryable"] is False


def test_cancel_unknown_job_is_404() -> None:
    response = _client().delete("/v1/jobs/nope")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"


def _succeeded_job(job_id: str) -> JobStatus:
    """A JobStatus in a state no production code path produces yet (no
    worker exists) — injected directly via store.put to exercise the result
    rendering/filtering branch of GET /v1/jobs/{id}/result."""

    transcript = Transcript(
        source_duration_seconds=10.0,
        segments=(
            Segment(
                id="s0",
                start_seconds=0.0,
                end_seconds=2.0,
                text="hello",
                speaker="spk_0",
            ),
            Segment(
                id="s1",
                start_seconds=2.0,
                end_seconds=5.0,
                text="world",
                speaker="spk_1",
            ),
            Segment(
                id="s2",
                start_seconds=5.0,
                end_seconds=9.0,
                text="again",
                speaker="spk_0",
            ),
        ),
    )
    return JobStatus(
        job_id=job_id,
        state=JobState.SUCCEEDED,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:01+00:00",
        config=PipelineConfig(),
        result=transcript,
    )


def test_result_renders_srt_for_succeeded_job() -> None:
    get_job_store().put(_succeeded_job("job_srt_test"))

    response = _client().get("/v1/jobs/job_srt_test/result?format=srt")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-subrip")
    assert "hello" in response.text
    assert "-->" in response.text


def test_result_default_format_is_json_and_matches_render_module() -> None:
    get_job_store().put(_succeeded_job("job_json_test"))

    response = _client().get("/v1/jobs/job_json_test/result")
    assert response.status_code == 200
    body = response.json()
    assert body["segments"][0]["text"] == "hello"
    assert body["source_duration_seconds"] == 10.0


def test_result_filters_by_speaker() -> None:
    get_job_store().put(_succeeded_job("job_speaker_test"))

    response = _client().get(
        "/v1/jobs/job_speaker_test/result?format=text&speaker=spk_1"
    )
    assert response.status_code == 200
    assert response.text.strip() == "world"


def test_result_filters_by_range() -> None:
    get_job_store().put(_succeeded_job("job_range_test"))

    response = _client().get(
        "/v1/jobs/job_range_test/result?format=text&start_seconds=3&end_seconds=4"
    )
    assert response.status_code == 200
    assert response.text.strip() == "world"
