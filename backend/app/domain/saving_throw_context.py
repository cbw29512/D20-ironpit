from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SavingThrowContext:
    """Immutable outcome context for a saving throw."""

    condition_id: str | None = None
