"""Tests for the whisper-street CLI.

Calls `main()` directly with an argv list — no subprocesses, no real server
starts. `serve` is verified by monkeypatching `uvicorn.run`.
"""

from __future__ import annotations

import dataclasses
import json
from typing import Any

import pytest

from whisper_street.cli.__main__ import main
from whisper_street.core.types import default_capabilities


def test_capabilities_matches_api_source_of_truth(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["capabilities"])

    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    expected = json.loads(json.dumps(dataclasses.asdict(default_capabilities())))
    assert payload == expected
    assert payload == {
        "models": [],
        "languages": [],
        "output_formats": ["json", "text", "srt", "vtt"],
        "max_file_size_bytes": 536_870_912,
        "max_audio_duration_seconds": 3600,
        "max_concurrent_jobs_per_caller": 2,
        "request_rate_limit_per_minute": 60,
        "result_retention_seconds": 0,
        "url_fetch_enabled": False,
    }


def test_transcribe_reports_stub_without_traceback(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["transcribe", "some.wav"])

    assert exit_code == 1
    captured = capsys.readouterr()
    message = captured.err.lower()
    assert "not implemented" in message or "no implementation" in message
    assert "roadmap" in message
    assert "Traceback (most recent call last)" not in captured.out
    assert "Traceback (most recent call last)" not in captured.err


def test_transcribe_accepts_all_documented_flags(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # This should still hit the ingest stub, but must not fail argument
    # parsing for any documented flag.
    exit_code = main(
        [
            "transcribe",
            "some.wav",
            "--format",
            "srt",
            "--language",
            "en",
            "--model",
            "tiny",
            "--no-isolation",
            "--diarize",
            "--word-timestamps",
        ]
    )

    assert exit_code == 1


def test_serve_invokes_uvicorn_run_with_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, Any]] = []

    def fake_run(app: str, **kwargs: Any) -> None:
        calls.append({"app": app, **kwargs})

    monkeypatch.setattr("uvicorn.run", fake_run)

    exit_code = main(["serve", "--port", "9001"])

    assert exit_code == 0
    assert len(calls) == 1
    call = calls[0]
    assert call["app"] == "whisper_street.api.app:create_app"
    assert call["factory"] is True
    assert call["port"] == 9001
    assert call["host"] == "127.0.0.1"


def test_serve_default_port(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_run(app: str, **kwargs: Any) -> None:
        calls.append({"app": app, **kwargs})

    monkeypatch.setattr("uvicorn.run", fake_run)

    exit_code = main(["serve"])

    assert exit_code == 0
    assert calls[0]["port"] == 8000


def test_no_subcommand_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "usage" in captured.out.lower()


def test_help_flag_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["-h"])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "usage" in captured.out.lower()


def test_unknown_subcommand_exits_two(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["not-a-real-command"])

    assert exit_code == 2
