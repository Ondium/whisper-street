"""Wires the five stages into a single run.

The Pipeline itself has no logic beyond calling its stages in order and
assembling their outputs into a Transcript — see docs/architecture.md#stages
for what each stage owns. Swapping a stage means constructing a Pipeline
with a different implementation of that stage's Protocol; nothing here
needs to change.
"""

from __future__ import annotations

from dataclasses import dataclass

from whisper_street.core.stages import (
    Emitter,
    Ingester,
    Isolator,
    Segmenter,
    Transcriber,
)
from whisper_street.core.types import OutputFormat, PipelineConfig, Transcript
from whisper_street.stages.emit import DefaultEmitter
from whisper_street.stages.ingest import StubIngester
from whisper_street.stages.isolate import StubIsolator
from whisper_street.stages.segment import StubSegmenter
from whisper_street.stages.transcribe import StubTranscriber


@dataclass(frozen=True, slots=True)
class Pipeline:
    """A concrete pipeline: one implementation per stage.

    Attributes:
        ingester: Implements Ingester.
        isolator: Implements Isolator.
        segmenter: Implements Segmenter.
        transcriber: Implements Transcriber.
        emitter: Implements Emitter.
    """

    ingester: Ingester
    isolator: Isolator
    segmenter: Segmenter
    transcriber: Transcriber
    emitter: Emitter

    def run(self, source: str | bytes, config: PipelineConfig) -> Transcript:
        """Run all four processing stages in order and assemble the result.

        Args:
            source: A file path or URL, or raw audio bytes — passed
                straight to the ingester.
            config: Pipeline configuration, echoed back on the returned
                Transcript.

        Returns:
            The resulting Transcript. failed_spans is always empty here —
            this stub pipeline has no partial-failure handling yet; a real
            transcriber implementation is what would populate it.

        Raises:
            NotImplementedError: If any stage is still a stub (see
                whisper_street.stages and docs/ROADMAP.md).
        """

        audio, source_metadata = self.ingester.ingest(source)
        isolation_result = self.isolator.isolate(audio, config)
        spans = self.segmenter.segment(isolation_result.audio, config)
        segments = self.transcriber.transcribe(isolation_result.audio, spans, config)
        return Transcript(
            source_duration_seconds=source_metadata.original_duration_seconds,
            language=config.language,
            segments=segments,
            config=config,
        )

    def emit(self, transcript: Transcript, fmt: OutputFormat) -> str:
        """Render `transcript` as `fmt` using this pipeline's emitter.

        Args:
            transcript: The transcript to render.
            fmt: The desired output format.

        Returns:
            The rendered transcript as a string.
        """

        return self.emitter.emit(transcript, fmt)


def default_pipeline() -> Pipeline:
    """Build the pipeline wired to today's default implementations.

    Every stage but emit is a stub (whisper_street.stages) — calling
    `.run()` on the result raises NotImplementedError at the ingest stage.
    Emit is real: it delegates to whisper_street.core.render.

    Returns:
        A Pipeline ready to run once its stub stages are replaced.
    """

    return Pipeline(
        ingester=StubIngester(),
        isolator=StubIsolator(),
        segmenter=StubSegmenter(),
        transcriber=StubTranscriber(),
        emitter=DefaultEmitter(),
    )
