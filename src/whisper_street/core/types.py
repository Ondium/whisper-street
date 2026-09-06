"""Data contracts shared by every pipeline stage.

**Timestamp rule (see docs/architecture.md#timestamps):** every field named
``*_seconds`` is a float number of seconds measured from the start of the
*original source media* — never from the start of a segment, a stage's
internal buffer, or a resampled clip. A stage may use a different origin
internally, but must convert back to this rule before the value crosses a
stage boundary.

These are plain, frozen dataclasses, not pydantic models: this module is
imported by the CLI, the API, and the MCP server alike, and none of them
should have to agree on a validation framework to share a transcript.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, TypeAlias

Seconds: TypeAlias = float
"""A duration or timestamp in seconds, as a float. See the module docstring
for the origin convention."""

StageName = Literal["ingest", "isolate", "segment", "transcribe", "emit"]
"""The five pipeline stages, in run order. See docs/architecture.md#stages."""

OutputFormat = Literal["json", "text", "srt", "vtt"]
"""A transcript rendering. ``json`` is canonical; the rest are derived from
it (docs/architecture.md#emit)."""


@dataclass(frozen=True, slots=True)
class Word:
    """A single recognized word with its timing.

    Attributes:
        text: The recognized word, as produced by the transcriber.
        start_seconds: Start of the word, in seconds from the start of the
            source media.
        end_seconds: End of the word, in seconds from the start of the
            source media. Must be >= start_seconds.
        confidence: Model confidence in [0.0, 1.0], or None if the backend
            does not report word-level confidence.
    """

    text: str
    start_seconds: Seconds
    end_seconds: Seconds
    confidence: float | None = None


@dataclass(frozen=True, slots=True)
class Segment:
    """A contiguous span of transcribed speech, optionally attributed to a
    speaker.

    Attributes:
        id: Stable identifier for this segment, unique within its transcript.
        start_seconds: Start of the segment, in seconds from the start of
            the source media.
        end_seconds: End of the segment, in seconds from the start of the
            source media. Must be >= start_seconds.
        text: The segment's transcribed text.
        words: Word-level timings within the segment, in order. Empty when
            the pipeline ran with segment-level granularity
            (PipelineConfig.timestamp_granularity == "segment").
        speaker: Speaker label, or None if diarization did not run or could
            not attribute this segment.
        confidence: Model confidence in [0.0, 1.0], or None if the backend
            does not report segment-level confidence.
        language: BCP-47-ish language code the segment was recognized as, or
            None if the backend does not report per-segment language.
    """

    id: str
    start_seconds: Seconds
    end_seconds: Seconds
    text: str
    words: tuple[Word, ...] = ()
    speaker: str | None = None
    confidence: float | None = None
    language: str | None = None


@dataclass(frozen=True, slots=True)
class SpeechSpan:
    """A span where the segmenter found speech, before transcription.

    Attributes:
        start_seconds: Start of the span, in seconds from the start of the
            source media.
        end_seconds: End of the span, in seconds from the start of the
            source media. Must be >= start_seconds.
        speaker: Speaker label from diarization, or None if diarization is
            disabled or did not attribute this span.
    """

    start_seconds: Seconds
    end_seconds: Seconds
    speaker: str | None = None


@dataclass(frozen=True, slots=True)
class AudioBuffer:
    """Decoded PCM audio passed between stages.

    Attributes:
        samples: The decoded PCM sample data. Left untyped deliberately —
            this is a stub contract, and the concrete representation (numpy
            array, bytes, array.array, ...) is an implementation decision
            for whichever ingest backend lands first.
        sample_rate_hz: Sample rate in hertz.
        channels: Number of interleaved audio channels.
    """

    samples: Any
    sample_rate_hz: int
    channels: int


@dataclass(frozen=True, slots=True)
class SourceMetadata:
    """Facts about the original source media, captured at ingest.

    Attributes:
        original_duration_seconds: Duration of the source media, in seconds,
            before any resampling or trimming.
        original_codec: Name of the source audio codec (e.g. "pcm_s16le",
            "aac", "opus"), as reported by the decoder.
        original_channels: Channel count of the source media, before any
            downmixing.
        original_sample_rate_hz: Sample rate of the source media in hertz,
            before any resampling.
        source_uri: Where the audio came from (file path or URL), or None
            if it arrived as an in-memory byte stream with no addressable
            origin.
    """

    original_duration_seconds: Seconds
    original_codec: str
    original_channels: int
    original_sample_rate_hz: int
    source_uri: str | None = None


@dataclass(frozen=True, slots=True)
class IsolationResult:
    """Output of the isolate stage.

    Attributes:
        audio: The isolated speech audio.
        removed: The audio that was removed (noise, music, other speakers),
            or None if the isolator does not retain it. Retaining this is
            what makes a bad transcript traceable to a specific stage; see
            docs/architecture.md#isolate.
    """

    audio: AudioBuffer
    removed: AudioBuffer | None


class JobState(str, Enum):
    """Lifecycle states of an asynchronous job. See
    docs/api/README.md#job-lifecycle for the transition diagram.

    Values are lowercase strings because they cross the HTTP API boundary
    directly as JSON.
    """

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class FailedSpan:
    """A span of audio that a stage could not process, in an otherwise
    usable (PARTIAL) result.

    Attributes:
        start_seconds: Start of the failed span, in seconds from the start
            of the source media.
        end_seconds: End of the failed span, in seconds from the start of
            the source media. Must be >= start_seconds.
        stage: Which pipeline stage the failure occurred in.
        reason: Human-readable explanation of what went wrong. Not a stable
            machine-readable code — see PipelineError for that.
    """

    start_seconds: Seconds
    end_seconds: Seconds
    stage: StageName
    reason: str


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Everything about how a transcript was produced. Configuration is a
    value, not a code path — see docs/architecture.md#configuration — so a
    result is only comparable to another result alongside the config that
    made it, which is why Transcript embeds one.

    Attributes:
        isolation_enabled: Whether the isolate stage runs at all.
        isolation_profile: Named isolation aggressiveness/behavior profile.
            Backend-defined; "default" is the only name this contract
            requires to exist.
        diarization_enabled: Whether the segment stage attempts speaker
            attribution.
        timestamp_granularity: "segment" returns segment-level timing only;
            "word" additionally populates Segment.words.
        language: Expected/forced language code, or None to auto-detect.
        model: Name of the transcription model/backend, or None to use the
            deployment default.
        output_formats: Which renderings to produce for this job.
    """

    isolation_enabled: bool = True
    isolation_profile: str = "default"
    diarization_enabled: bool = False
    timestamp_granularity: Literal["segment", "word"] = "segment"
    language: str | None = None
    model: str | None = None
    output_formats: tuple[OutputFormat, ...] = ("json",)


@dataclass(frozen=True, slots=True)
class Transcript:
    """The canonical result of a pipeline run. Every other rendering (text,
    SRT, VTT) is derived from this — see whisper_street.core.render and
    docs/architecture.md#emit.

    Attributes:
        schema_version: Schema version of this shape. Bumped only on a
            breaking change to the JSON rendering, per
            docs/api/README.md#compatibility.
        source_duration_seconds: Duration of the original source media, in
            seconds.
        language: Language the transcript was produced in, or None if
            unknown/undetected.
        segments: Transcribed segments, in chronological order.
        config: The configuration that produced this transcript.
        failed_spans: Spans that failed during processing. Non-empty implies
            the owning job's state is JobState.PARTIAL.
    """

    schema_version: Literal[1] = 1
    source_duration_seconds: Seconds = 0.0
    language: str | None = None
    segments: tuple[Segment, ...] = ()
    config: PipelineConfig = field(default_factory=PipelineConfig)
    failed_spans: tuple[FailedSpan, ...] = ()


@dataclass(frozen=True, slots=True)
class Capabilities:
    """What a deployment can actually do — the payload for
    ``GET /v1/capabilities`` (docs/api/README.md). Exists so a client
    doesn't have to assume; it can ask.

    Attributes:
        models: Transcription model names this deployment offers.
        languages: Language codes this deployment supports.
        output_formats: Renderings this deployment can produce.
        max_file_size_bytes: Largest accepted upload, in bytes.
        max_audio_duration_seconds: Longest accepted source media duration,
            in seconds.
        max_concurrent_jobs_per_caller: Concurrent job limit per caller.
        request_rate_limit_per_minute: Request rate limit per caller, per
            minute.
        result_retention_seconds: How long a completed result is retained
            before deletion, in seconds. 0 means not retained past
            delivery.
        url_fetch_enabled: Whether this deployment fetches audio from a
            caller-supplied URL. See docs/api/README.md#submitting-a-job for
            why this defaults to disabled.
    """

    models: tuple[str, ...]
    languages: tuple[str, ...]
    output_formats: tuple[OutputFormat, ...]
    max_file_size_bytes: int
    max_audio_duration_seconds: Seconds
    max_concurrent_jobs_per_caller: int
    request_rate_limit_per_minute: int
    result_retention_seconds: int
    url_fetch_enabled: bool


@dataclass(frozen=True, slots=True)
class PipelineError:
    """A structured, actionable error — see docs/api/README.md#errors.

    Attributes:
        code: Stable machine-readable error code. Clients branch on this;
            it does not change across a major API version.
        message: Human-readable explanation. May be reworded; not stable.
        retryable: Whether retrying the same request could succeed.
        field: The request field or parameter at fault, or None if the
            error isn't attributable to a single field.
    """

    code: str
    message: str
    retryable: bool
    field: str | None = None


@dataclass(frozen=True, slots=True)
class JobStatus:
    """Status and, when available, result of an asynchronous job — the
    payload for ``GET /v1/jobs/{id}`` (docs/api/README.md).

    Attributes:
        job_id: Opaque job identifier.
        state: Current lifecycle state.
        created_at: ISO 8601 timestamp of job creation.
        updated_at: ISO 8601 timestamp of the last state change.
        config: The configuration this job was submitted with.
        result: The transcript, once state is SUCCEEDED or PARTIAL.
            None otherwise.
        failed_spans: Spans that failed during processing. Non-empty implies
            state is PARTIAL.
        error: Present when state is FAILED; None otherwise.
    """

    job_id: str
    state: JobState
    created_at: str
    updated_at: str
    config: PipelineConfig
    result: Transcript | None = None
    failed_spans: tuple[FailedSpan, ...] = ()
    error: PipelineError | None = None


def default_capabilities() -> Capabilities:
    """The capabilities of an unconfigured deployment.

    This is the single source of truth for default limits — the HTTP API
    and CLI both import it rather than repeating the numbers, so the
    published `/v1/capabilities` response and any local default can't drift
    apart by accident.

    Returns:
        A Capabilities with no models/languages configured yet (this stub
        has no backend wired in), conservative-but-usable limits (512 MiB
        upload, 1 hour of audio, 2 concurrent jobs per caller, 60 requests
        per minute, no result retention), and URL fetch disabled.
    """

    return Capabilities(
        models=(),
        languages=(),
        output_formats=("json", "text", "srt", "vtt"),
        max_file_size_bytes=536_870_912,
        max_audio_duration_seconds=3600,
        max_concurrent_jobs_per_caller=2,
        request_rate_limit_per_minute=60,
        result_retention_seconds=0,
        url_fetch_enabled=False,
    )
