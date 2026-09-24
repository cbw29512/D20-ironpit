from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SavingThrowContext:
    """Immutable incoming-effect semantics checked against defender-owned buffs."""

    condition_id: str | None = None
    magical_effect: bool = False
    source_is_spell: bool = False
    source_creature_type: str | None = None
    effect_tags: frozenset[str] = frozenset()
