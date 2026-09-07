"""Command-line entry point for whisper-street.

Exposes three subcommands:

- ``capabilities`` — print this deployment's capabilities as JSON, the same
  payload as ``GET /v1/capabilities`` (docs/api/README.md). Both the CLI and
  the HTTP API read from whisper_street.core.types.default_capabilities so
  they cannot drift apart.
- ``transcribe`` — run the pipeline against a local audio file. Every stage
  but emit is currently a stub (whisper_street.stages), so this raises a
  clear, non-traceback error until a real ingest/isolate/segment/transcribe
  implementation lands; see docs/ROADMAP.md.
- ``serve`` — run the HTTP API with uvicorn. uvicorn and the API app are
  imported lazily, inside the serve handler, so that `capabilities` and
  `transcribe` do not pay the cost of importing FastAPI and do not require
  the API package to exist.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from typing import get_args

from whisper_street.core.pipeline import default_pipeline
from whisper_street.core.types import OutputFormat, PipelineConfig, default_capabilities

_OUTPUT_FORMATS: tuple[OutputFormat, ...] = get_args(OutputFormat)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser and its subcommands.

    Returns:
        An ArgumentParser with the ``capabilities``, ``transcribe``, and
        ``serve`` subcommands attached under the ``command`` dest.
    """

    parser = argparse.ArgumentParser(
        prog="whisper-street",
        description="Voice isolation and transcription pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "capabilities",
        help="Print this deployment's capabilities as JSON.",
    )

    transcribe_parser = subparsers.add_parser(
        "transcribe",
        help="Transcribe a local audio file.",
    )
    transcribe_parser.add_argument("path", help="Path to the audio file.")
    transcribe_parser.add_argument(
        "--format",
        choices=_OUTPUT_FORMATS,
        default="json",
        help="Output rendering to produce (default: json).",
    )
    transcribe_parser.add_argument(
        "--language",
        default=None,
        help="Expected/forced language code (default: auto-detect).",
    )
    transcribe_parser.add_argument(
        "--model",
        default=None,
        help="Transcription model/backend name (default: deployment default).",
    )
    transcribe_parser.add_argument(
        "--no-isolation",
        dest="isolation_enabled",
        action="store_false",
        default=True,
        help="Skip the isolate stage.",
    )
    transcribe_parser.add_argument(
        "--diarize",
        dest="diarization_enabled",
        action="store_true",
        default=False,
        help="Attempt speaker attribution.",
    )
    transcribe_parser.add_argument(
        "--word-timestamps",
        dest="word_timestamps",
        action="store_true",
        default=False,
        help="Populate word-level timings, not just segment-level.",
    )

    serve_parser = subparsers.add_parser(
        "serve",
        help="Run the HTTP API.",
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host/interface to bind (default: 127.0.0.1).",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind (default: 8000).",
    )

    return parser


def _run_capabilities() -> int:
    """Print `default_capabilities()` as JSON, matching `GET /v1/capabilities`.

    Returns:
        Exit code 0, always.
    """

    print(json.dumps(dataclasses.asdict(default_capabilities())))
    return 0


def _run_transcribe(args: argparse.Namespace) -> int:
    """Run the pipeline against `args.path` and print the rendered result.

    Args:
        args: Parsed `transcribe` subcommand arguments.

    Returns:
        0 on success. 1 if a pipeline stage is still a stub — the
        NotImplementedError is caught and reported as a one-line message on
        stderr, never as a raw traceback.
    """

    config = PipelineConfig(
        isolation_enabled=args.isolation_enabled,
        diarization_enabled=args.diarization_enabled,
        timestamp_granularity="word" if args.word_timestamps else "segment",
        language=args.language,
        model=args.model,
        output_formats=(args.format,),
    )

    pipeline = default_pipeline()
    try:
        transcript = pipeline.run(args.path, config)
    except NotImplementedError as exc:
        print(f"whisper-street: transcription failed - {exc}", file=sys.stderr)
        return 1

    print(pipeline.emit(transcript, args.format))
    return 0


def _run_serve(args: argparse.Namespace) -> int:
    """Run the HTTP API with uvicorn, binding to `args.host`/`args.port`.

    uvicorn is imported here rather than at module scope so that
    `capabilities` and `transcribe` never require it to import successfully.

    Args:
        args: Parsed `serve` subcommand arguments.

    Returns:
        0. In practice `uvicorn.run` blocks until the server shuts down.
    """

    import uvicorn

    uvicorn.run(
        "whisper_street.api.app:create_app",
        host=args.host,
        port=args.port,
        factory=True,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Argument vector, excluding the program name. None to use
            `sys.argv[1:]`.

    Returns:
        Process exit code: 0 on success or on `-h`/no subcommand (help is
        printed), 2 on an argument-parsing error (argparse's default), 1 if
        `transcribe` hit a stub stage.
    """

    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "capabilities":
        return _run_capabilities()
    if args.command == "transcribe":
        return _run_transcribe(args)
    return _run_serve(args)


if __name__ == "__main__":
    raise SystemExit(main())
