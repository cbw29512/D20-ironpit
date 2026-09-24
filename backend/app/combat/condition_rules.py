from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.domain.models import CombatantState

BLINDED = "blinded"
INCAPACITATED = "incapacitated"
PARALYZED = "paralyzed"
PETRIFIED = "petrified"
RESTRAINED = "restrained"
STUNNED = "stunned"


def has_condition(state: CombatantState, condition_id: str) -> bool:
    if condition_id not in state.active_effect_ids:
        return False
    timed = [effect for effect in state.timed_effects if effect.effect_id == condition_id]
    if timed:
        return any(
            not condition_is_immune(
                state,
                condition_id,
                source_is_magical=effect.source_is_magical,
            )
            for effect in timed
        )
    return not condition_is_immune(state, condition_id)


def is_incapacitated(state: CombatantState) -> bool:
    if condition_is_immune(state, INCAPACITATED):
        return False
    return (
        state.is_unconscious
        or has_condition(state, INCAPACITATED)
        or has_condition(state, PARALYZED)
        or has_condition(state, PETRIFIED)
        or has_condition(state, STUNNED)
    )


def automatically_fails_strength_dexterity_save(state: CombatantState) -> bool:
    return (
        state.is_unconscious
        or has_condition(state, PARALYZED)
        or has_condition(state, PETRIFIED)
        or has_condition(state, STUNNED)
    )


def attacks_have_advantage_against(state: CombatantState) -> bool:
    return (
        state.is_unconscious
        or has_condition(state, BLINDED)
        or has_condition(state, PARALYZED)
        or has_condition(state, PETRIFIED)
        or has_condition(state, STUNNED)
    )


def close_hit_is_automatic_critical(state: CombatantState) -> bool:
    return state.is_unconscious or has_condition(state, PARALYZED)


def condition_speed_is_zero(state: CombatantState) -> bool:
    return (
        state.is_unconscious
        or has_condition(state, PARALYZED)
        or has_condition(state, PETRIFIED)
        or has_condition(state, RESTRAINED)
    )
