"""Stage contracts, as structural types (Protocol).

A stage is defined by its signature, not by inheritance — any object with
the right method is a valid stage, which is what makes stages swappable
(docs/architecture.md#the-idea). Concrete implementations live under
whisper_street.stages; today they're all stubs.
"""

from __future__ import annotations

from typing import Protocol

from whisper_street.core.types import (
    AudioBuffer,
    IsolationResult,
    OutputFormat,
    PipelineConfig,
    Segment,
    SourceMetadata,
    SpeechSpan,
    Transcript,
)


class Ingester(Protocol):
    """Accepts whatever the caller has and produces a known-shape audio
    buffer. See docs/architecture.md#ingest."""

    def ingest(self, source: str | bytes) -> tuple[AudioBuffer, SourceMetadata]:
        """Decode a source into PCM audio plus its original metadata.

        Args:
            source: A file path or URL, or raw audio bytes.

        Returns:
            The decoded audio buffer and metadata describing the source
            before any resampling.
        """
        ...


class Isolator(Protocol):
    """Separates speech from everything that isn't the speech you want. See
    docs/architecture.md#isolate."""

    def isolate(self, audio: AudioBuffer, config: PipelineConfig) -> IsolationResult:
        """Isolate speech in `audio` according to `config`.

        Args:
            audio: Normalized PCM audio from the ingest stage.
            config: Pipeline configuration; isolation_enabled and
                isolation_profile govern this stage's behavior.

        Returns:
            The isolated speech audio, plus whatever was removed.
        """
        ...


class Segmenter(Protocol):
    """Decides where speech is, and who is speaking. See
    docs/architecture.md#segment."""

    def segment(
        self, audio: AudioBuffer, config: PipelineConfig
    ) -> tuple[SpeechSpan, ...]:
        """Find speech spans in isolated `audio`.

        Args:
            audio: Isolated speech audio.
            config: Pipeline configuration; diarization_enabled governs
                whether returned spans carry speaker labels.

        Returns:
            Speech spans in chronological order, timestamped in seconds
            from the start of the source media.
        """
        ...


class Transcriber(Protocol):
    """Turns speech into text with timings. See
    docs/architecture.md#transcribe."""

    def transcribe(
        self,
        audio: AudioBuffer,
        spans: tuple[SpeechSpan, ...],
        config: PipelineConfig,
    ) -> tuple[Segment, ...]:
        """Transcribe the speech within `spans` of `audio`.

        Args:
            audio: Isolated speech audio.
            spans: Speech spans to transcribe, from the segment stage.
            config: Pipeline configuration; model, language, and
                timestamp_granularity govern this stage's behavior.

        Returns:
            Transcribed segments, in chronological order, timestamped in
            seconds from the start of the source media.
        """
        ...


class Emitter(Protocol):
    """Renders a transcript in the form a consumer needs. See
    docs/architecture.md#emit."""

    def emit(self, transcript: Transcript, fmt: OutputFormat) -> str:
        """Render `transcript` as `fmt`.

        Args:
            transcript: The canonical transcript to render.
            fmt: The desired output format.

        Returns:
            The rendered transcript as a string.
        """
        ...
