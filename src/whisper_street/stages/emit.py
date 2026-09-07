"""The real Emitter. Unlike the other stages, emit has nothing left to
decide once a Transcript exists — it's a pure rendering, implemented in
whisper_street.core.render. See docs/architecture.md#emit."""

from __future__ import annotations

import json

from whisper_street.core.render import to_json, to_srt, to_text, to_vtt
from whisper_street.core.stages import Emitter
from whisper_street.core.types import OutputFormat, Transcript


class DefaultEmitter(Emitter):
    """Renders a Transcript by delegating to whisper_street.core.render."""

    def emit(self, transcript: Transcript, fmt: OutputFormat) -> str:
        """Render `transcript` as `fmt`.

        Args:
            transcript: The canonical transcript to render.
            fmt: One of "json", "text", "srt", "vtt".

        Returns:
            The rendered transcript as a string. JSON is serialized with
            the standard library `json` module.

        Raises:
            ValueError: If `fmt` is not one of the four known formats.
        """

        if fmt == "json":
            return json.dumps(to_json(transcript))
        if fmt == "text":
            return to_text(transcript)
        if fmt == "srt":
            return to_srt(transcript)
        if fmt == "vtt":
            return to_vtt(transcript)
        raise ValueError(
            f"emit: unknown output format {fmt!r}; "
            "expected one of 'json', 'text', 'srt', 'vtt'"
        )
