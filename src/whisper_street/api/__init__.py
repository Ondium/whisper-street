"""The whisper-street HTTP API — see docs/api/README.md for the contract.

This package is the FastAPI implementation of that design. Everything here
is bookkeeping: job creation, lookup, cancellation, and result rendering.
No stage but ``emit`` (whisper_street.core.render) is implemented yet, so
anything that would actually run the pipeline surfaces
``PIPELINE_NOT_IMPLEMENTED`` (see whisper_street.api.errors).
"""

from __future__ import annotations

API_VERSION = "0.1.0"
"""Version reported by GET /v1/health and set as the FastAPI app version."""
