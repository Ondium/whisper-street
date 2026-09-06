"""FastAPI dependency providers for the API layer.

Kept deliberately thin: each function returns something a route needs,
constructed from whisper_street.core so the API never redefines pipeline
wiring or default limits.
"""

from __future__ import annotations

from whisper_street.api.jobs_store import InMemoryJobStore
from whisper_street.core.pipeline import Pipeline, default_pipeline
from whisper_street.core.types import Capabilities, default_capabilities

_job_store = InMemoryJobStore()
"""Process-wide singleton. One store per process is correct today: there is
no worker and no persistence layer, so there is nothing to shard or scope
per-request."""


def get_job_store() -> InMemoryJobStore:
    """Return the process-wide job store singleton."""

    return _job_store


def get_capabilities() -> Capabilities:
    """Return this deployment's capabilities (whisper_street.core.types)."""

    return default_capabilities()


def get_pipeline() -> Pipeline:
    """Build a pipeline wired to today's default (stub) stage implementations."""

    return default_pipeline()
