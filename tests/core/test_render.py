from whisper_street.core.render import to_json, to_srt, to_text, to_vtt
from whisper_street.core.types import (
    FailedSpan,
    PipelineConfig,
    Segment,
    Transcript,
    Word,
)


def _sample_transcript() -> Transcript:
    segment_0 = Segment(
        id="s0",
        start_seconds=0.0,
        end_seconds=1.5,
        text="Hello world",
        words=(
            Word(text="Hello", start_seconds=0.0, end_seconds=0.5, confidence=0.99),
            Word(text="world", start_seconds=0.6, end_seconds=1.5, confidence=0.95),
        ),
        speaker="spk_0",
        confidence=0.9,
        language="en",
    )
    # start/end cross the one-hour mark to exercise hour rollover formatting.
    segment_1 = Segment(
        id="s1",
        start_seconds=3661.25,
        end_seconds=3662.999,
        text="Second segment",
    )
    failed_span = FailedSpan(
        start_seconds=10.0,
        end_seconds=12.0,
        stage="transcribe",
        reason="model timeout",
    )
    config = PipelineConfig(
        isolation_enabled=False,
        language="en",
        output_formats=("json", "srt"),
    )
    return Transcript(
        source_duration_seconds=3663.0,
        language="en",
        segments=(segment_0, segment_1),
        config=config,
        failed_spans=(failed_span,),
    )


def test_to_json_shape_and_values() -> None:
    data = to_json(_sample_transcript())

    assert data["schema_version"] == 1
    assert data["source_duration_seconds"] == 3663.0
    assert data["language"] == "en"

    assert data["config"] == {
        "isolation_enabled": False,
        "isolation_profile": "default",
        "diarization_enabled": False,
        "timestamp_granularity": "segment",
        "language": "en",
        "model": None,
        "output_formats": ["json", "srt"],
    }

    assert len(data["segments"]) == 2
    segment_0 = data["segments"][0]
    assert segment_0["id"] == "s0"
    assert segment_0["start_seconds"] == 0.0
    assert segment_0["end_seconds"] == 1.5
    assert segment_0["text"] == "Hello world"
    assert segment_0["speaker"] == "spk_0"
    assert segment_0["confidence"] == 0.9
    assert segment_0["language"] == "en"
    assert segment_0["words"] == [
        {"text": "Hello", "start_seconds": 0.0, "end_seconds": 0.5, "confidence": 0.99},
        {"text": "world", "start_seconds": 0.6, "end_seconds": 1.5, "confidence": 0.95},
    ]

    segment_1 = data["segments"][1]
    assert segment_1["speaker"] is None
    assert segment_1["words"] == []

    assert data["failed_spans"] == [
        {
            "start_seconds": 10.0,
            "end_seconds": 12.0,
            "stage": "transcribe",
            "reason": "model timeout",
        }
    ]


def test_to_json_empty_transcript() -> None:
    data = to_json(Transcript())
    assert data["segments"] == []
    assert data["failed_spans"] == []


def test_to_text_joins_segment_text_with_newlines() -> None:
    assert to_text(_sample_transcript()) == "Hello world\nSecond segment"


def test_to_text_empty_transcript_is_empty_string() -> None:
    assert to_text(Transcript()) == ""


def test_to_srt_formats_timestamps_and_indexes_cues() -> None:
    srt = to_srt(_sample_transcript())
    assert srt == (
        "1\n"
        "00:00:00,000 --> 00:00:01,500\n"
        "Hello world\n"
        "\n"
        "2\n"
        "01:01:01,250 --> 01:01:02,999\n"
        "Second segment\n"
    )


def test_to_srt_empty_transcript_is_empty_string() -> None:
    assert to_srt(Transcript()) == ""


def test_to_vtt_has_header_and_dot_separated_millis() -> None:
    vtt = to_vtt(_sample_transcript())
    assert vtt == (
        "WEBVTT\n"
        "\n"
        "1\n"
        "00:00:00.000 --> 00:00:01.500\n"
        "Hello world\n"
        "\n"
        "2\n"
        "01:01:01.250 --> 01:01:02.999\n"
        "Second segment\n"
    )


def test_to_vtt_empty_transcript_is_header_only() -> None:
    assert to_vtt(Transcript()) == "WEBVTT\n\n"
