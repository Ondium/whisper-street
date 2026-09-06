"""`POST /v1/transcribe` — synchronous processing, short audio only.

See docs/api/README.md#proposed-surface. Every stage but `emit` is a stub
(whisper_street.stages), so `Pipeline.run` always raises NotImplementedError
today, at the ingest stage — this endpoint's only real job right now is to
turn that into a structured 501.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from whisper_street.api.deps import get_pipeline
from whisper_street.api.errors import ApiError
from whisper_street.api.schemas import JobSubmission, render_transcript
from whisper_street.core.pipeline import Pipeline

router = APIRouter()


@router.post("/transcribe")
async def transcribe(
    submission: JobSubmission,
    pipeline: Pipeline = Depends(get_pipeline),
) -> Response:
    """Run the pipeline synchronously and return the rendered result.

    Returns:
        The transcript rendered as `submission.output_formats[0]`
        (default "json").

    Raises:
        ApiError: VALIDATION_ERROR (422) if neither `audio` nor `source_url`
            is set; PIPELINE_NOT_IMPLEMENTED (501) if any stage the pipeline
            calls is still a stub (true for every deployment today).
    """

    if submission.audio is None and submission.source_url is None:
        raise ApiError(
            422,
            "VALIDATION_ERROR",
            "One of 'audio' or 'source_url' is required.",
            field="audio",
        )

    try:
        transcript = pipeline.run(submission.source(), submission.to_pipeline_config())
    except NotImplementedError as exc:
        raise ApiError(
            501, "PIPELINE_NOT_IMPLEMENTED", str(exc), retryable=False
        ) from exc

    fmt = submission.output_formats[0] if submission.output_formats else "json"
    body, media_type = render_transcript(transcript, fmt)
    return Response(content=body, media_type=media_type)
