from __future__ import annotations

from app.domain.models import CombatantState


def effective_max_hp(state: CombatantState) -> int:
    """Return the combatant's current Hit Point maximum, including active maximum-HP increases."""
    return state.template.max_hp + state.max_hp_bonus
