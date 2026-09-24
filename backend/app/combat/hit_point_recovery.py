from __future__ import annotations

from app.combat.hit_points import effective_max_hp
from app.combat.zero_hp_state import reset_death_saves
from app.domain.models import CombatantState
from app.domain.traits import CombatTrait


def restore_hit_points(state: CombatantState, amount: int) -> int:
    """Restore true HP; ordinary healing cannot restore a dead creature or a Swarm."""
    if amount < 0:
        raise ValueError("Healing cannot be negative.")
    if state.is_dead or amount == 0 or CombatTrait.SWARM in state.template.combat_traits:
        return 0
    before = state.current_hp
    state.current_hp = min(effective_max_hp(state), before + amount)
    healed = state.current_hp - before
    if healed > 0:
        state.is_alive = True
        state.is_unconscious = False
        state.is_stable = False
        reset_death_saves(state)
    return healed
