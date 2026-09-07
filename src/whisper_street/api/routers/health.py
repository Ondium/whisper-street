"""`GET /v1/health` — liveness and readiness.

See docs/api/README.md#proposed-surface. `ready` reflects whether the
API/job-lifecycle contract itself is functional, not whether a real
transcription engine is available — that is communicated separately via
`GET /v1/capabilities` returning an empty `models` list.
"""

from __future__ import annotations

from fastapi import APIRouter

from whisper_street.api import API_VERSION

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, object]:
    """Report liveness and readiness.

    Returns:
        `{"status": "ok", "live": True, "ready": True, "version": API_VERSION}`.
    """

    return {"status": "ok", "live": True, "ready": True, "version": API_VERSION}
