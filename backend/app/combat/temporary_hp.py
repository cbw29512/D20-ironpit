from __future__ import annotations

from app.domain.models import CombatantState
from app.domain.traits import CombatTrait


def grant_temporary_hit_points(state: CombatantState, amount: int) -> int:
    if amount < 0:
        raise ValueError("Temporary Hit Points cannot be negative.")
    if CombatTrait.SWARM in state.template.combat_traits:
        return state.temporary_hp
    state.temporary_hp = max(state.temporary_hp, amount)
    return state.temporary_hp
