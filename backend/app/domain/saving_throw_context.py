from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SavingThrowContext:
    """Immutable outcome context for a saving throw."""

    condition_id: str | None = None
    magical_effect: bool = False
    spell_effect: bool = False
    source_creature_type: str | None = None
