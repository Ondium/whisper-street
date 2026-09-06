"""`GET /v1/capabilities` — what this deployment can actually do.

See docs/api/README.md#proposed-surface and
whisper_street.core.types.default_capabilities.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from whisper_street.api.deps import get_capabilities
from whisper_street.api.schemas import capabilities_to_dict
from whisper_street.core.types import Capabilities

router = APIRouter()


@router.get("/capabilities")
async def get_capabilities_endpoint(
    capabilities: Capabilities = Depends(get_capabilities),
) -> dict[str, object]:
    """Report this deployment's capabilities.

    Returns:
        The serialized Capabilities (whisper_street.api.schemas.capabilities_to_dict).
    """

    return capabilities_to_dict(capabilities)
