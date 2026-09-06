"""Structured error responses — see docs/api/README.md#errors.

Every error response is
``{"error": {"code": str, "message": str, "field": str | None, "retryable": bool}}``.
`code` is the stable, machine-readable part of the contract; `message` may be
reworded freely.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """An error with an HTTP status and a stable machine-readable code.

    Attributes:
        status_code: HTTP status code to respond with.
        code: Stable machine-readable error code (docs/api/README.md#errors).
        message: Human-readable explanation. Not stable; may be reworded.
        retryable: Whether retrying the same request could succeed.
        field: The request field or parameter at fault, or None if the
            error isn't attributable to a single field.
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        retryable: bool = False,
        field: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.retryable = retryable
        self.field = field


def _error_body(
    code: str, message: str, retryable: bool, field: str | None
) -> dict[str, Any]:
    """Build the structured error response body."""

    return {
        "error": {
            "code": code,
            "message": message,
            "field": field,
            "retryable": retryable,
        }
    }


async def _handle_api_error(request: Request, exc: Exception) -> JSONResponse:
    """Render an ApiError as its structured JSON body."""

    assert isinstance(exc, ApiError)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.code, exc.message, exc.retryable, exc.field),
    )


async def _handle_not_implemented(request: Request, exc: Exception) -> JSONResponse:
    """Map a bare NotImplementedError (any stub stage, see
    whisper_street.core.errors) to 501 PIPELINE_NOT_IMPLEMENTED."""

    assert isinstance(exc, NotImplementedError)
    return JSONResponse(
        status_code=501,
        content=_error_body("PIPELINE_NOT_IMPLEMENTED", str(exc), False, None),
    )


async def _handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
    """Map FastAPI/pydantic request validation failures to 422 VALIDATION_ERROR,
    carrying the offending field when pydantic identifies one."""

    assert isinstance(exc, RequestValidationError)
    field: str | None = None
    errors = exc.errors()
    if errors:
        location = [str(part) for part in errors[0].get("loc", ())]
        parts = [part for part in location if part not in ("body", "query", "path")]
        field = ".".join(parts) if parts else None
    return JSONResponse(
        status_code=422,
        content=_error_body(
            "VALIDATION_ERROR", "Request validation failed.", False, field
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register this module's exception handlers on `app`.

    Args:
        app: The FastAPI application to register handlers on.
    """

    app.add_exception_handler(ApiError, _handle_api_error)
    app.add_exception_handler(NotImplementedError, _handle_not_implemented)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
