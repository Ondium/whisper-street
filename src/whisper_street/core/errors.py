"""The one error stub implementations raise.

Kept to a single function deliberately: every stub stage should fail the
same way, with the same pointers to where the real contract and the import
plan live, so a caller hitting NotImplementedError anywhere in this package
gets the same next step.
"""

from __future__ import annotations

from typing import NoReturn

from whisper_street.core.types import StageName

__all__ = ["StageName", "stub"]


def stub(stage: StageName) -> NoReturn:
    """Raise for a pipeline stage that has no implementation yet.

    Args:
        stage: The stage being called.

    Raises:
        NotImplementedError: Always. The message names `stage` and points
            to its contract in docs/architecture.md and the import plan in
            docs/ROADMAP.md.
    """

    raise NotImplementedError(
        f"whisper-street: the '{stage}' stage has no implementation yet. "
        f"Contract: docs/architecture.md#{stage}. "
        "Import plan: docs/ROADMAP.md."
    )
