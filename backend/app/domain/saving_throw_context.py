from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SavingThrowContext:
    """Immutable incoming-effect semantics checked against defender-owned buffs."""

    condition_id: str | None = None
    magical_effect: bool = False
    effect_tags: frozenset[str] = frozenset()
