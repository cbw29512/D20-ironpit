from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)
BLINDED = "blinded"
INCAPACITATED = "incapacitated"
PARALYZED = "paralyzed"
PETRIFIED = "petrified"
RESTRAINED = "restrained"
STUNNED = "stunned"


def has_condition(state: CombatantState, condition_id: str) -> bool:
    try:
        swallowed = state.swallowed
        swallowed_applies = swallowed is not None and condition_id in swallowed.applied_condition_ids
        return (
            (condition_id in state.active_effect_ids or swallowed_applies)
            and not condition_is_immune(state, condition_id)
        )
    except Exception as exc:
        logger.exception("Failed to inspect condition %s for %s.", condition_id, state.template.name)
        raise RuntimeError("Condition state could not be evaluated.") from exc


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