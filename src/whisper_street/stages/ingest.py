"""Stub Ingester. See docs/architecture.md#ingest for the contract this must
satisfy once implemented, and docs/ROADMAP.md for the import plan."""

from __future__ import annotations

from whisper_street.core.errors import stub
from whisper_street.core.stages import Ingester
from whisper_street.core.types import AudioBuffer, SourceMetadata


class StubIngester(Ingester):
    """Placeholder Ingester. Every call raises NotImplementedError."""

    def ingest(self, source: str | bytes) -> tuple[AudioBuffer, SourceMetadata]:
        stub("ingest")
