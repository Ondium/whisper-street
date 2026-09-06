"""Job lifecycle endpoints — see docs/api/README.md#job-lifecycle.

`POST /v1/jobs` only ever produces a QUEUED job: there is no worker yet to
advance it (whisper_street.api.jobs_store.InMemoryJobStore). Every other
state a job can be in (running, succeeded, partial, failed) is reachable
today only by a test injecting a JobStatus directly via `store.put`.
"""

from __future__ import annotations

from dataclasses import replace

from fastapi import APIRouter, Depends, Query, Response

from whisper_street.api.deps import get_job_store
from whisper_street.api.errors import ApiError
from whisper_street.api.jobs_store import InMemoryJobStore
from whisper_street.api.schemas import (
    JobSubmission,
    job_status_to_dict,
    render_transcript,
)
from whisper_street.core.types import JobState, OutputFormat, Transcript

router = APIRouter()


def _require_audio_or_source_url(submission: JobSubmission) -> None:
    if submission.audio is None and submission.source_url is None:
        raise ApiError(
            422,
            "VALIDATION_ERROR",
            "One of 'audio' or 'source_url' is required.",
            field="audio",
        )


@router.post("/jobs", status_code=202)
async def create_job(
    submission: JobSubmission,
    store: InMemoryJobStore = Depends(get_job_store),
) -> dict[str, object]:
    """Submit audio for processing. See docs/api/README.md#submitting-a-job.

    Returns:
        202 with the new JobStatus, state "queued".

    Raises:
        ApiError: VALIDATION_ERROR (422) if neither `audio` nor `source_url`
            is set.
    """

    _require_audio_or_source_url(submission)
    status = store.create(submission.to_pipeline_config())
    return job_status_to_dict(status)


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str, store: InMemoryJobStore = Depends(get_job_store)
) -> dict[str, object]:
    """Fetch a job's status.

    Returns:
        The JobStatus.

    Raises:
        ApiError: JOB_NOT_FOUND (404) if `job_id` is unknown.
    """

    status = store.get(job_id)
    if status is None:
        raise ApiError(
            404, "JOB_NOT_FOUND", f"No job with id '{job_id}'.", field="job_id"
        )
    return job_status_to_dict(status)


@router.delete("/jobs/{job_id}")
async def cancel_job(
    job_id: str, store: InMemoryJobStore = Depends(get_job_store)
) -> dict[str, object]:
    """Cancel a job, or delete a retained result.

    Returns:
        The updated JobStatus, state "cancelled".

    Raises:
        ApiError: JOB_NOT_FOUND (404) if `job_id` is unknown.
    """

    status = store.cancel(job_id)
    if status is None:
        raise ApiError(
            404, "JOB_NOT_FOUND", f"No job with id '{job_id}'.", field="job_id"
        )
    return job_status_to_dict(status)


def _filter_transcript(
    transcript: Transcript,
    start_seconds: float | None,
    end_seconds: float | None,
    speaker: str | None,
) -> Transcript:
    """Keep only segments overlapping [start_seconds, end_seconds] and/or
    attributed to `speaker`. Any filter left None is not applied."""

    segments = transcript.segments
    if start_seconds is not None:
        segments = tuple(s for s in segments if s.end_seconds >= start_seconds)
    if end_seconds is not None:
        segments = tuple(s for s in segments if s.start_seconds <= end_seconds)
    if speaker is not None:
        segments = tuple(s for s in segments if s.speaker == speaker)
    return replace(transcript, segments=segments)


@router.get("/jobs/{job_id}/result")
async def get_job_result(
    job_id: str,
    format: OutputFormat = Query("json"),
    start_seconds: float | None = Query(None),
    end_seconds: float | None = Query(None),
    speaker: str | None = Query(None),
    store: InMemoryJobStore = Depends(get_job_store),
) -> Response:
    """Fetch a completed job's result in a requested rendering.

    Args:
        job_id: The job identifier.
        format: Desired rendering. Defaults to "json".
        start_seconds: If set, drop segments ending before this time.
        end_seconds: If set, drop segments starting after this time.
        speaker: If set, keep only segments attributed to this speaker.
        store: Injected job store.

    Returns:
        The rendered transcript with the matching media type.

    Raises:
        ApiError: JOB_NOT_FOUND (404) if `job_id` is unknown;
            JOB_CANCELLED (409, not retryable) if the job was cancelled;
            JOB_NOT_COMPLETE (409, retryable) if the job has no result yet.
    """

    status = store.get(job_id)
    if status is None:
        raise ApiError(
            404, "JOB_NOT_FOUND", f"No job with id '{job_id}'.", field="job_id"
        )

    if status.state is JobState.CANCELLED:
        raise ApiError(409, "JOB_CANCELLED", "Job was cancelled.", retryable=False)
    if status.result is None:
        raise ApiError(
            409, "JOB_NOT_COMPLETE", "Job has not completed yet.", retryable=True
        )

    transcript = status.result
    if start_seconds is not None or end_seconds is not None or speaker is not None:
        transcript = _filter_transcript(transcript, start_seconds, end_seconds, speaker)

    body, media_type = render_transcript(transcript, format)
    return Response(content=body, media_type=media_type)
