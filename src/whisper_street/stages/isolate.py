"""Stub Isolator. See docs/architecture.md#isolate for the contract this must
satisfy once implemented, and docs/ROADMAP.md for the import plan."""

from __future__ import annotations

from whisper_street.core.errors import stub
from whisper_street.core.stages import Isolator
from whisper_street.core.types import AudioBuffer, IsolationResult, PipelineConfig


class StubIsolator(Isolator):
    """Placeholder Isolator. Every call raises NotImplementedError."""

    def isolate(self, audio: AudioBuffer, config: PipelineConfig) -> IsolationResult:
        stub("isolate")
