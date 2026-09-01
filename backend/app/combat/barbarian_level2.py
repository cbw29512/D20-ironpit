from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.timed_conditions import apply_timed_condition
from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)
RECKLESS_ATTACK_EFFECT_ID = "reckless-attack"


def danger_sense_advantage(state: CombatantState, ability: str) -> int:
    """Return one Advantage source for certified Barbarian Danger Sense."""
    try:
        enabled = state.template.progression_features.danger_sense
        return int(enabled and ability == "dexterity" and not is_incapacitated(state))
    except Exception as exc:
        logger.exception("Danger Sense resolution failed for %s.", state.template.name)
        raise RuntimeError("Danger Sense could not be resolved.") from exc


def reckless_attack_active(state: CombatantState) -> bool:
    try:
        return RECKLESS_ATTACK_EFFECT_ID in state.active_effect_ids
    except Exception as exc:
        logger.exception("Reckless Attack state check failed for %s.", state.template.name)
        raise RuntimeError("Reckless Attack state could not be read.") from exc


def activate_reckless_attack(
    state: CombatantState,
    attack: WeaponAttack,
    actor_id: str,
    round_number: int,
) -> bool:
    """Choose Reckless Attack on the first eligible Strength attack roll of the turn."""
    try:
        if not state.template.progression_features.reckless_attack:
            return False
        if attack.attack_ability != "strength" or reckless_attack_active(state):
            return False
        applied = apply_timed_condition(
            state,
            RECKLESS_ATTACK_EFFECT_ID,
            actor_id,
            source_effect_id=RECKLESS_ATTACK_EFFECT_ID,
            applied_round=round_number,
            expires_round=round_number + 1,
            expiry_timing="source_turn_start",
        )
        return applied == RECKLESS_ATTACK_EFFECT_ID
    except Exception as exc:
        logger.exception("Reckless Attack activation failed for %s.", state.template.name)
        raise RuntimeError("Reckless Attack could not be activated.") from exc


def reckless_attack_advantage(state: CombatantState, attack: WeaponAttack) -> int:
    """Return one Advantage source for Strength attack rolls while Reckless Attack is active."""
    try:
        return int(reckless_attack_active(state) and attack.attack_ability == "strength")
    except Exception as exc:
        logger.exception("Reckless Attack advantage failed for %s.", state.template.name)
        raise RuntimeError("Reckless Attack advantage could not be resolved.") from exc


def attacks_against_reckless_advantage(state: CombatantState) -> int:
    """Attack rolls against a reckless Barbarian have Advantage until its next turn starts."""
    try:
        return int(reckless_attack_active(state))
    except Exception as exc:
        logger.exception("Reckless Attack defense effect failed for %s.", state.template.name)
        raise RuntimeError("Reckless Attack defense effect could not be resolved.") from exc
