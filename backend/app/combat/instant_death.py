from __future__ import annotations

from collections.abc import Iterable

from app.combat.concentration import end_concentration_if_incapacitated
from app.domain.runtime import CombatantState


DODGE_EFFECT_ID = "dodge"


def apply_instant_death(
    state: CombatantState,
    affected_states: Iterable[CombatantState] | None = None,
) -> bool:
    """Kill a creature without dealing damage or invoking zero-HP prevention."""
    if state.is_dead:
        return False
    state.current_hp = 0
    state.temporary_hp = 0
    state.is_alive = False
    state.is_dead = True
    state.is_unconscious = False
    state.is_stable = False
    state.active_effect_ids = [effect for effect in state.active_effect_ids if effect != DODGE_EFFECT_ID]
    end_concentration_if_incapacitated(state, affected_states)
    return True
