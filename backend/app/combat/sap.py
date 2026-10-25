from __future__ import annotations

import logging

from app.combat.timed_condition_apply import apply_timed_condition
from app.combat.timed_condition_lifecycle import remove_effect_instance
from app.combat.weapon_mastery import weapon_mastery_active
from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)

WEAPON_SAP_EFFECT_ID = "weapon-mastery-sap"
TACTICAL_MASTER_SAP_EFFECT_ID = "tactical-master-sap"
SAP_EFFECT_IDS = frozenset({WEAPON_SAP_EFFECT_ID, TACTICAL_MASTER_SAP_EFFECT_ID})


def apply_sap_effect(
    attacker_id: str,
    target: CombatantState,
    round_number: int,
    *,
    effect_id: str,
    source_effect_id: str,
) -> bool:
    try:
        if target.is_dead or target.current_hp <= 0:
            return False
        return apply_timed_condition(
            target,
            effect_id,
            attacker_id,
            source_effect_id=source_effect_id,
            applied_round=round_number,
            expires_round=round_number + 1,
            expiry_timing="source_turn_start",
        ) is not None
    except Exception:
        logger.exception(
            "Failed to apply Sap effect %s from %s to %s.",
            effect_id,
            attacker_id,
            target.template.name,
        )
        raise


def weapon_sap_eligible(
    state: CombatantState,
    attack: WeaponAttack,
) -> bool:
    try:
        return weapon_mastery_active(state, attack, "Sap")
    except Exception:
        logger.exception(
            "Failed to evaluate Sap eligibility for %s using %s.",
            state.template.name,
            attack.id,
        )
        raise


def apply_weapon_sap(
    attacker: CombatantState,
    attacker_id: str,
    target: CombatantState,
    attack: WeaponAttack,
    round_number: int,
) -> bool:
    try:
        if not weapon_sap_eligible(attacker, attack):
            return False
        return apply_sap_effect(
            attacker_id,
            target,
            round_number,
            effect_id=WEAPON_SAP_EFFECT_ID,
            source_effect_id="weapon-mastery",
        )
    except Exception:
        logger.exception(
            "Failed to apply weapon Sap from %s to %s.",
            attacker_id,
            target.template.name,
        )
        raise


def sap_disadvantage(state: CombatantState) -> int:
    try:
        return int(
            any(
                effect.effect_id in SAP_EFFECT_IDS
                for effect in state.timed_effects
            )
        )
    except Exception:
        logger.exception(
            "Failed to evaluate Sap disadvantage for %s.",
            state.template.name,
        )
        raise


def consume_sap(state: CombatantState) -> int:
    try:
        effects = [
            effect
            for effect in list(state.timed_effects)
            if effect.effect_id in SAP_EFFECT_IDS
        ]
        for effect in effects:
            remove_effect_instance(state, effect)
        return len(effects)
    except Exception:
        logger.exception(
            "Failed to consume Sap effects for %s.",
            state.template.name,
        )
        raise
