from __future__ import annotations

from app.domain.models import CombatantState


def effective_max_hp(state: CombatantState) -> int:
    """Return the combatant's current Hit Point maximum after active increases and reductions."""
    return max(0, state.template.max_hp + state.max_hp_bonus - state.max_hp_reduction)


def set_positive_hit_points(state: CombatantState, amount: int) -> int:
    """Enter the shared positive-HP state after healing, recovery, or a survive-at-1 effect."""
    if amount <= 0:
        raise ValueError("Positive Hit Points must be greater than zero.")
    current = min(effective_max_hp(state), amount)
    if current <= 0:
        raise ValueError("A combatant with a 0 Hit Point maximum cannot enter a positive-HP state.")
    state.current_hp = current
    state.is_alive = True
    state.is_dead = False
    state.is_unconscious = False
    state.is_stable = False
    state.death_save_successes = 0
    state.death_save_failures = 0
    return current
