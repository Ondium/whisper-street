"""FastAPI application factory.

Uvicorn target: `whisper_street.api.app:create_app` (run with `--factory`).
"""

from __future__ import annotations

from fastapi import FastAPI

from whisper_street.api import API_VERSION
from whisper_street.api.errors import register_exception_handlers
from whisper_street.api.routers import capabilities, health, jobs, transcribe


def create_app() -> FastAPI:
    """Build the whisper-street API app.

    Registers every router under `/v1` (docs/api/README.md#proposed-surface)
    and the structured-error exception handlers
    (whisper_street.api.errors.register_exception_handlers).

    Returns:
        A ready-to-serve FastAPI application.
    """

    app = FastAPI(title="whisper-street API", version=API_VERSION)
    register_exception_handlers(app)
    app.include_router(health.router, prefix="/v1")
    app.include_router(capabilities.router, prefix="/v1")
    app.include_router(jobs.router, prefix="/v1")
    app.include_router(transcribe.router, prefix="/v1")
    return app
