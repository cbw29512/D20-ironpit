from __future__ import annotations

from app.combat.exhaustion import max_hp_after_exhaustion
from app.domain.models import CombatantState


def effective_max_hp(state: CombatantState) -> int:
    """Return the current HP maximum after active bonuses and edition-specific exhaustion."""
    maximum = state.template.max_hp + state.max_hp_bonus
    return max_hp_after_exhaustion(state, maximum)
