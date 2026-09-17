from __future__ import annotations

from app.domain.models import CombatantState


def effective_max_hp(state: CombatantState) -> int:
    """Return current Hit Point maximum after generic bonuses and 2014 Exhaustion."""
    maximum = state.template.max_hp + state.max_hp_bonus
    if state.exhaustion_level_2014 >= 4:
        maximum //= 2
    return max(1, maximum)
