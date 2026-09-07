"""Stub Transcriber. See docs/architecture.md#transcribe for the contract
this must satisfy once implemented, and docs/ROADMAP.md for the import
plan."""

from __future__ import annotations

from whisper_street.core.errors import stub
from whisper_street.core.stages import Transcriber
from whisper_street.core.types import (
    AudioBuffer,
    PipelineConfig,
    Segment,
    SpeechSpan,
)


class StubTranscriber(Transcriber):
    """Placeholder Transcriber. Every call raises NotImplementedError."""

    def transcribe(
        self,
        audio: AudioBuffer,
        spans: tuple[SpeechSpan, ...],
        config: PipelineConfig,
    ) -> tuple[Segment, ...]:
        stub("transcribe")
