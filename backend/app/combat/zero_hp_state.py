from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.combat.hit_points import effective_max_hp
from app.domain.models import CombatantState

DODGE_EFFECT_ID = "dodge"
PRONE_EFFECT_ID = "prone"


def reset_death_saves(state: CombatantState) -> None:
    state.death_save_successes = 0
    state.death_save_failures = 0


def mark_dead(state: CombatantState) -> str:
    state.current_hp = 0
    state.is_alive = False
    state.is_dead = True
    state.is_unconscious = False
    state.is_stable = False
    state.active_effect_ids = [
        effect for effect in state.active_effect_ids
        if effect != DODGE_EFFECT_ID
    ]
    return "dead"


def mark_unconscious(state: CombatantState) -> str:
    state.is_alive = True
    state.is_unconscious = True
    state.is_stable = False
    state.active_effect_ids = [
        effect for effect in state.active_effect_ids
        if effect != DODGE_EFFECT_ID
    ]
    if (
        not condition_is_immune(state, PRONE_EFFECT_ID)
        and PRONE_EFFECT_ID not in state.active_effect_ids
    ):
        state.active_effect_ids.append(PRONE_EFFECT_ID)
    return "unconscious"


def damage_at_zero(
    state: CombatantState,
    incoming: int,
    *,
    critical: bool,
) -> str:
    if state.template.kind == "monster" or incoming >= effective_max_hp(state):
        return mark_dead(state)
    state.is_stable = False
    state.death_save_failures = min(
        3,
        state.death_save_failures + (2 if critical else 1),
    )
    if state.death_save_failures >= 3:
        return mark_dead(state)
    return mark_unconscious(state)
