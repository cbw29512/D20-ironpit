from __future__ import annotations

import logging

from app.combat.timed_conditions import apply_timed_condition
from app.domain.models import CombatTrait, CombatantState, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)
RECKLESS_ATTACK_EFFECT_ID = "reckless-attack"


def _has_reckless(state: CombatantState) -> bool:
    try:
        return state.template.progression_features.reckless_attack or CombatTrait.RECKLESS in state.template.combat_traits
    except Exception as exc:
        logger.exception("Reckless capability check failed for %s.", state.template.name)
        raise RuntimeError("Reckless capability could not be read.") from exc


def reckless_attack_active(state: CombatantState) -> bool:
    try:
        return RECKLESS_ATTACK_EFFECT_ID in state.active_effect_ids
    except Exception as exc:
        logger.exception("Reckless Attack state check failed for %s.", state.template.name)
        raise RuntimeError("Reckless Attack state could not be read.") from exc


def _eligible_attack(state: CombatantState, attack: WeaponAttack) -> bool:
    if attack.attack_ability != "strength":
        return False
    return state.template.ruleset != "2014" or attack.weapon.attack_kind is WeaponAttackKind.MELEE


def activate_reckless_attack(
    state: CombatantState,
    attack: WeaponAttack,
    actor_id: str,
    round_number: int,
) -> bool:
    """Choose Reckless Attack on the first edition-eligible Strength attack roll of the active turn."""
    try:
        if not _has_reckless(state):
            return False
        if not _eligible_attack(state, attack) or reckless_attack_active(state):
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
    """Return one Advantage source for eligible attacks while Reckless Attack is active."""
    try:
        return int(reckless_attack_active(state) and _eligible_attack(state, attack))
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
