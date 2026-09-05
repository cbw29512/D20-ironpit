from __future__ import annotations

from app.domain.models import CombatantState


def effective_max_hp(state: CombatantState) -> int:
    """Return the combatant's current Hit Point maximum after active increases and reductions."""
    return max(0, state.template.max_hp + state.max_hp_bonus - state.max_hp_reduction)
