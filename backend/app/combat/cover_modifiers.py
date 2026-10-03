from __future__ import annotations

from app.domain.modifiers import ModifierKind
from app.domain.runtime import CombatantState


def strongest_cover_bonus(
    state: CombatantState,
    kind: ModifierKind,
    ability: str | None = None,
) -> int:
    """Return the single strongest applicable cover benefit."""
    return max(
        (
            item.flat_bonus
            for item in state.active_modifiers
            if item.kind is kind
            and (item.save_ability is None or ability is None or item.save_ability == ability)
        ),
        default=0,
    )
