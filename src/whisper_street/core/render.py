"""Renderings of a Transcript.

JSON is canonical (docs/architecture.md#emit); text, SRT, and VTT are all
derived from it here, using only the standard library. Every function takes
timestamps as seconds-from-source-start floats (docs/architecture.md#timestamps)
and converts them to whatever the target format needs.
"""

from __future__ import annotations

from typing import Any

from whisper_street.core.types import Seconds, Transcript


def to_json(transcript: Transcript) -> dict[str, Any]:
    """Render `transcript` as the canonical JSON-able dict.

    Args:
        transcript: The transcript to render.

    Returns:
        A dict of only JSON-safe types (str, int, float, bool, None, list,
        dict) with the shape::

            {
                "schema_version": int,
                "source_duration_seconds": float,
                "language": str | None,
                "config": {
                    "isolation_enabled": bool,
                    "isolation_profile": str,
                    "diarization_enabled": bool,
                    "timestamp_granularity": str,
                    "language": str | None,
                    "model": str | None,
                    "output_formats": list[str],
                },
                "segments": [
                    {
                        "id": str,
                        "start_seconds": float,
                        "end_seconds": float,
                        "text": str,
                        "speaker": str | None,
                        "confidence": float | None,
                        "language": str | None,
                        "words": [
                            {
                                "text": str,
                                "start_seconds": float,
                                "end_seconds": float,
                                "confidence": float | None,
                            },
                            ...
                        ],
                    },
                    ...
                ],
                "failed_spans": [
                    {
                        "start_seconds": float,
                        "end_seconds": float,
                        "stage": str,
                        "reason": str,
                    },
                    ...
                ],
            }
    """

    config = transcript.config
    return {
        "schema_version": transcript.schema_version,
        "source_duration_seconds": transcript.source_duration_seconds,
        "language": transcript.language,
        "config": {
            "isolation_enabled": config.isolation_enabled,
            "isolation_profile": config.isolation_profile,
            "diarization_enabled": config.diarization_enabled,
            "timestamp_granularity": config.timestamp_granularity,
            "language": config.language,
            "model": config.model,
            "output_formats": list(config.output_formats),
        },
        "segments": [
            {
                "id": segment.id,
                "start_seconds": segment.start_seconds,
                "end_seconds": segment.end_seconds,
                "text": segment.text,
                "speaker": segment.speaker,
                "confidence": segment.confidence,
                "language": segment.language,
                "words": [
                    {
                        "text": word.text,
                        "start_seconds": word.start_seconds,
                        "end_seconds": word.end_seconds,
                        "confidence": word.confidence,
                    }
                    for word in segment.words
                ],
            }
            for segment in transcript.segments
        ],
        "failed_spans": [
            {
                "start_seconds": failed_span.start_seconds,
                "end_seconds": failed_span.end_seconds,
                "stage": failed_span.stage,
                "reason": failed_span.reason,
            }
            for failed_span in transcript.failed_spans
        ],
    }


def to_text(transcript: Transcript) -> str:
    """Render `transcript` as plain text: each segment's text, one per line.

    Args:
        transcript: The transcript to render.

    Returns:
        Segment texts joined with "\\n". Empty string if there are no
        segments.
    """

    return "\n".join(segment.text for segment in transcript.segments)


def _split_hh_mm_ss_ms(seconds: Seconds) -> tuple[int, int, int, int]:
    """Split a seconds-from-source-start float into whole hours, minutes,
    seconds, and milliseconds, rounding to the nearest millisecond."""

    total_ms = round(seconds * 1000)
    hours, remainder_ms = divmod(total_ms, 3_600_000)
    minutes, remainder_ms = divmod(remainder_ms, 60_000)
    secs, millis = divmod(remainder_ms, 1000)
    return hours, minutes, secs, millis


def _format_srt_timestamp(seconds: Seconds) -> str:
    """Format `seconds` as an SRT timestamp: HH:MM:SS,mmm."""

    hours, minutes, secs, millis = _split_hh_mm_ss_ms(seconds)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _format_vtt_timestamp(seconds: Seconds) -> str:
    """Format `seconds` as a WebVTT timestamp: HH:MM:SS.mmm."""

    hours, minutes, secs, millis = _split_hh_mm_ss_ms(seconds)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def to_srt(transcript: Transcript) -> str:
    """Render `transcript` as SubRip (SRT).

    Args:
        transcript: The transcript to render.

    Returns:
        SRT text: one 1-indexed cue per segment, each cue formatted as
        ``index\\ntimestamp --> timestamp\\ntext``, separated by a blank
        line, with a trailing newline. Empty string if there are no
        segments.
    """

    if not transcript.segments:
        return ""

    blocks = [
        f"{index}\n"
        f"{_format_srt_timestamp(segment.start_seconds)} --> "
        f"{_format_srt_timestamp(segment.end_seconds)}\n"
        f"{segment.text}"
        for index, segment in enumerate(transcript.segments, start=1)
    ]
    return "\n\n".join(blocks) + "\n"


def to_vtt(transcript: Transcript) -> str:
    """Render `transcript` as WebVTT.

    Args:
        transcript: The transcript to render.

    Returns:
        VTT text: a "WEBVTT" header line followed by a blank line, then one
        1-indexed cue per segment, each cue formatted as
        ``index\\ntimestamp --> timestamp\\ntext``, separated by a blank
        line, with a trailing newline. "WEBVTT\\n\\n" alone if there are no
        segments.
    """

    header = "WEBVTT\n\n"
    if not transcript.segments:
        return header

    blocks = [
        f"{index}\n"
        f"{_format_vtt_timestamp(segment.start_seconds)} --> "
        f"{_format_vtt_timestamp(segment.end_seconds)}\n"
        f"{segment.text}"
        for index, segment in enumerate(transcript.segments, start=1)
    ]
    return header + "\n\n".join(blocks) + "\n"
