from whisper_street.core.types import (
    AudioBuffer,
    Capabilities,
    FailedSpan,
    IsolationResult,
    JobState,
    JobStatus,
    PipelineConfig,
    PipelineError,
    Segment,
    SourceMetadata,
    SpeechSpan,
    Transcript,
    Word,
    default_capabilities,
)


def test_word_construction_and_defaults() -> None:
    word = Word(text="hi", start_seconds=0.0, end_seconds=0.5)
    assert word.text == "hi"
    assert word.start_seconds == 0.0
    assert word.end_seconds == 0.5
    assert word.confidence is None


def test_segment_construction_and_defaults() -> None:
    segment = Segment(id="s0", start_seconds=0.0, end_seconds=1.0, text="hi")
    assert segment.words == ()
    assert segment.speaker is None
    assert segment.confidence is None
    assert segment.language is None

    word = Word(text="hi", start_seconds=0.0, end_seconds=1.0, confidence=0.9)
    full = Segment(
        id="s1",
        start_seconds=0.0,
        end_seconds=1.0,
        text="hi",
        words=(word,),
        speaker="spk_0",
        confidence=0.95,
        language="en",
    )
    assert full.words == (word,)
    assert full.speaker == "spk_0"


def test_speech_span_defaults() -> None:
    span = SpeechSpan(start_seconds=0.0, end_seconds=1.0)
    assert span.speaker is None


def test_audio_buffer_holds_arbitrary_samples() -> None:
    buffer = AudioBuffer(samples=[0, 1, 2], sample_rate_hz=16_000, channels=1)
    assert buffer.samples == [0, 1, 2]
    assert buffer.sample_rate_hz == 16_000
    assert buffer.channels == 1


def test_source_metadata_defaults() -> None:
    metadata = SourceMetadata(
        original_duration_seconds=10.0,
        original_codec="pcm_s16le",
        original_channels=2,
        original_sample_rate_hz=44_100,
    )
    assert metadata.source_uri is None


def test_isolation_result_allows_no_removed_audio() -> None:
    audio = AudioBuffer(samples=b"", sample_rate_hz=16_000, channels=1)
    result = IsolationResult(audio=audio, removed=None)
    assert result.removed is None


def test_job_state_values_are_lowercase() -> None:
    assert JobState.QUEUED.value == "queued"
    assert JobState.RUNNING.value == "running"
    assert JobState.SUCCEEDED.value == "succeeded"
    assert JobState.PARTIAL.value == "partial"
    assert JobState.FAILED.value == "failed"
    assert JobState.CANCELLED.value == "cancelled"
    assert JobState.QUEUED == "queued"


def test_failed_span_fields() -> None:
    failed_span = FailedSpan(
        start_seconds=1.0, end_seconds=2.0, stage="transcribe", reason="timeout"
    )
    assert failed_span.stage == "transcribe"
    assert failed_span.reason == "timeout"


def test_pipeline_config_defaults() -> None:
    config = PipelineConfig()
    assert config.isolation_enabled is True
    assert config.isolation_profile == "default"
    assert config.diarization_enabled is False
    assert config.timestamp_granularity == "segment"
    assert config.language is None
    assert config.model is None
    assert config.output_formats == ("json",)


def test_transcript_defaults() -> None:
    transcript = Transcript()
    assert transcript.schema_version == 1
    assert transcript.source_duration_seconds == 0.0
    assert transcript.language is None
    assert transcript.segments == ()
    assert transcript.config == PipelineConfig()
    assert transcript.failed_spans == ()


def test_pipeline_error_defaults() -> None:
    error = PipelineError(code="bad_request", message="nope", retryable=False)
    assert error.field is None


def test_job_status_defaults() -> None:
    status = JobStatus(
        job_id="job_0",
        state=JobState.QUEUED,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
        config=PipelineConfig(),
    )
    assert status.result is None
    assert status.failed_spans == ()
    assert status.error is None


def test_default_capabilities_values() -> None:
    capabilities = default_capabilities()
    assert isinstance(capabilities, Capabilities)
    assert capabilities.models == ()
    assert capabilities.languages == ()
    assert capabilities.output_formats == ("json", "text", "srt", "vtt")
    assert capabilities.max_file_size_bytes == 536_870_912
    assert capabilities.max_audio_duration_seconds == 3600
    assert capabilities.max_concurrent_jobs_per_caller == 2
    assert capabilities.request_rate_limit_per_minute == 60
    assert capabilities.result_retention_seconds == 0
    assert capabilities.url_fetch_enabled is False
