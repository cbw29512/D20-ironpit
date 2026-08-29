from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.domain.models import CombatantState

INCAPACITATED = "incapacitated"
PARALYZED = "paralyzed"
RESTRAINED = "restrained"
STUNNED = "stunned"


def has_condition(state: CombatantState, condition_id: str) -> bool:
    return condition_id in state.active_effect_ids and not condition_is_immune(state, condition_id)


def is_incapacitated(state: CombatantState) -> bool:
    if condition_is_immune(state, INCAPACITATED):
        return False
    return (
        state.is_unconscious
        or has_condition(state, INCAPACITATED)
        or has_condition(state, PARALYZED)
        or has_condition(state, STUNNED)
    )


def automatically_fails_strength_dexterity_save(state: CombatantState) -> bool:
    return state.is_unconscious or has_condition(state, PARALYZED) or has_condition(state, STUNNED)


def attacks_have_advantage_against(state: CombatantState) -> bool:
    return state.is_unconscious or has_condition(state, PARALYZED) or has_condition(state, STUNNED)


def close_hit_is_automatic_critical(state: CombatantState) -> bool:
    return state.is_unconscious or has_condition(state, PARALYZED)


def condition_speed_is_zero(state: CombatantState) -> bool:
    return state.is_unconscious or has_condition(state, PARALYZED) or has_condition(state, RESTRAINED)
