"""Stub Segmenter. See docs/architecture.md#segment for the contract this
must satisfy once implemented, and docs/ROADMAP.md for the import plan."""

from __future__ import annotations

from whisper_street.core.errors import stub
from whisper_street.core.stages import Segmenter
from whisper_street.core.types import AudioBuffer, PipelineConfig, SpeechSpan


class StubSegmenter(Segmenter):
    """Placeholder Segmenter. Every call raises NotImplementedError."""

    def segment(
        self, audio: AudioBuffer, config: PipelineConfig
    ) -> tuple[SpeechSpan, ...]:
        stub("segment")
