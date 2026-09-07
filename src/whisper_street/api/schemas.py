"""Request/response shapes for the API layer.

Requests: a minimal pydantic model (`JobSubmission`) — pydantic is already a
project dependency and buys real validation for free (type coercion, enum
checking) at the API boundary, which is exactly where it belongs.

Note on audio delivery: docs/api/README.md#submitting-a-job describes audio
arriving as a multipart upload or a source URL. True multipart parsing needs
the `python-multipart` package, which is not declared in pyproject.toml's
dependencies for this API — adding it is a dependency decision out of scope
for this stub. `audio` here is therefore an opaque string field in the JSON
body (e.g. a data URI or an internal reference) rather than a real file
upload; `source_url` is the documented alternative. Neither is read or
processed — no stage past `emit` exists yet (whisper_street.stages) — so this
only affects how a submission is bookkept, not any behavior.

Responses: whisper_street.core.types dataclasses are the source of truth;
this module only converts them to JSON-safe dicts. No response is mirrored
as a second pydantic model — that would just be a second definition of the
same shape to keep in sync.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel

from whisper_street.core import render
from whisper_street.core.types import (
    Capabilities,
    FailedSpan,
    JobStatus,
    OutputFormat,
    PipelineConfig,
    PipelineError,
    Transcript,
)


class JobSubmission(BaseModel):
    """A request body for `POST /v1/jobs` and `POST /v1/transcribe`.

    See the module docstring for why `audio` is an opaque string rather than
    a real file upload. At least one of `audio` or `source_url` must be set;
    that is enforced by the route, not here, so the error can carry a
    specific field name (see whisper_street.api.errors.ApiError).

    Attributes:
        audio: Opaque audio reference/payload, or None.
        source_url: URL the server would fetch audio from, or None. Recorded
            only — never fetched, since url fetching is disabled by default
            (docs/api/README.md#submitting-a-job).
        isolation_enabled: See PipelineConfig.isolation_enabled.
        isolation_profile: See PipelineConfig.isolation_profile.
        diarization_enabled: See PipelineConfig.diarization_enabled.
        timestamp_granularity: See PipelineConfig.timestamp_granularity.
        language: See PipelineConfig.language.
        model: See PipelineConfig.model.
        output_formats: See PipelineConfig.output_formats.
    """

    audio: str | None = None
    source_url: str | None = None
    isolation_enabled: bool = True
    isolation_profile: str = "default"
    diarization_enabled: bool = False
    timestamp_granularity: Literal["segment", "word"] = "segment"
    language: str | None = None
    model: str | None = None
    output_formats: tuple[OutputFormat, ...] = ("json",)

    def to_pipeline_config(self) -> PipelineConfig:
        """Build the PipelineConfig this submission describes."""

        return PipelineConfig(
            isolation_enabled=self.isolation_enabled,
            isolation_profile=self.isolation_profile,
            diarization_enabled=self.diarization_enabled,
            timestamp_granularity=self.timestamp_granularity,
            language=self.language,
            model=self.model,
            output_formats=self.output_formats,
        )

    def source(self) -> str | bytes:
        """The value to pass as `Pipeline.run`'s `source` argument.

        Returns:
            `source_url` if set, else `audio` (or "" if neither was given —
            callers should reject that case before reaching here).
        """

        if self.source_url is not None:
            return self.source_url
        return self.audio or ""


def config_to_dict(config: PipelineConfig) -> dict[str, Any]:
    """Serialize a PipelineConfig to a JSON-safe dict."""

    return {
        "isolation_enabled": config.isolation_enabled,
        "isolation_profile": config.isolation_profile,
        "diarization_enabled": config.diarization_enabled,
        "timestamp_granularity": config.timestamp_granularity,
        "language": config.language,
        "model": config.model,
        "output_formats": list(config.output_formats),
    }


def failed_span_to_dict(failed_span: FailedSpan) -> dict[str, Any]:
    """Serialize a FailedSpan to a JSON-safe dict."""

    return {
        "start_seconds": failed_span.start_seconds,
        "end_seconds": failed_span.end_seconds,
        "stage": failed_span.stage,
        "reason": failed_span.reason,
    }


def error_to_dict(error: PipelineError) -> dict[str, Any]:
    """Serialize a PipelineError to a JSON-safe dict."""

    return {
        "code": error.code,
        "message": error.message,
        "retryable": error.retryable,
        "field": error.field,
    }


def capabilities_to_dict(capabilities: Capabilities) -> dict[str, Any]:
    """Serialize a Capabilities to the `GET /v1/capabilities` response body."""

    return {
        "models": list(capabilities.models),
        "languages": list(capabilities.languages),
        "output_formats": list(capabilities.output_formats),
        "max_file_size_bytes": capabilities.max_file_size_bytes,
        "max_audio_duration_seconds": capabilities.max_audio_duration_seconds,
        "max_concurrent_jobs_per_caller": capabilities.max_concurrent_jobs_per_caller,
        "request_rate_limit_per_minute": capabilities.request_rate_limit_per_minute,
        "result_retention_seconds": capabilities.result_retention_seconds,
        "url_fetch_enabled": capabilities.url_fetch_enabled,
    }


def job_status_to_dict(status: JobStatus) -> dict[str, Any]:
    """Serialize a JobStatus to the `GET /v1/jobs/{id}` response body."""

    return {
        "job_id": status.job_id,
        "state": status.state.value,
        "created_at": status.created_at,
        "updated_at": status.updated_at,
        "config": config_to_dict(status.config),
        "result": render.to_json(status.result) if status.result is not None else None,
        "failed_spans": [failed_span_to_dict(span) for span in status.failed_spans],
        "error": error_to_dict(status.error) if status.error is not None else None,
    }


_RENDERERS: dict[OutputFormat, Callable[[Transcript], str]] = {
    "json": lambda transcript: json.dumps(render.to_json(transcript)),
    "text": render.to_text,
    "srt": render.to_srt,
    "vtt": render.to_vtt,
}

_MEDIA_TYPES: dict[OutputFormat, str] = {
    "json": "application/json",
    "text": "text/plain",
    "srt": "application/x-subrip",
    "vtt": "text/vtt",
}


def render_transcript(transcript: Transcript, fmt: OutputFormat) -> tuple[str, str]:
    """Render `transcript` as `fmt` for an HTTP response body.

    Args:
        transcript: The transcript to render.
        fmt: The desired output format.

    Returns:
        A (body, media_type) pair.
    """

    return _RENDERERS[fmt](transcript), _MEDIA_TYPES[fmt]
