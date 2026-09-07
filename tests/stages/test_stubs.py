import json

import pytest

from whisper_street.core.render import to_json
from whisper_street.core.types import AudioBuffer, PipelineConfig, Segment, Transcript
from whisper_street.stages.emit import DefaultEmitter
from whisper_street.stages.ingest import StubIngester
from whisper_street.stages.isolate import StubIsolator
from whisper_street.stages.segment import StubSegmenter
from whisper_street.stages.transcribe import StubTranscriber


def test_stub_ingester_raises() -> None:
    with pytest.raises(NotImplementedError, match="ingest"):
        StubIngester().ingest("source.wav")


def test_stub_isolator_raises() -> None:
    audio = AudioBuffer(samples=b"", sample_rate_hz=16_000, channels=1)
    with pytest.raises(NotImplementedError, match="isolate"):
        StubIsolator().isolate(audio, PipelineConfig())


def test_stub_segmenter_raises() -> None:
    audio = AudioBuffer(samples=b"", sample_rate_hz=16_000, channels=1)
    with pytest.raises(NotImplementedError, match="segment"):
        StubSegmenter().segment(audio, PipelineConfig())


def test_stub_transcriber_raises() -> None:
    audio = AudioBuffer(samples=b"", sample_rate_hz=16_000, channels=1)
    with pytest.raises(NotImplementedError, match="transcribe"):
        StubTranscriber().transcribe(audio, (), PipelineConfig())


def test_default_emitter_emit_matches_render_module() -> None:
    transcript = Transcript(
        segments=(Segment(id="s0", start_seconds=0.0, end_seconds=1.0, text="hi"),)
    )
    emitter = DefaultEmitter()

    assert emitter.emit(transcript, "text") == "hi"
    assert emitter.emit(transcript, "srt") == ("1\n00:00:00,000 --> 00:00:01,000\nhi\n")
    assert emitter.emit(transcript, "vtt") == (
        "WEBVTT\n\n1\n00:00:00.000 --> 00:00:01.000\nhi\n"
    )

    assert json.loads(emitter.emit(transcript, "json")) == to_json(transcript)


def test_default_emitter_rejects_unknown_format() -> None:
    transcript = Transcript()
    with pytest.raises(ValueError, match="unknown output format"):
        DefaultEmitter().emit(transcript, "xml")  # type: ignore[arg-type]
