from __future__ import annotations

import logging

from app.combat.sap import TACTICAL_MASTER_SAP_EFFECT_ID, apply_sap_effect
from app.combat.tactical_master_policy import tactical_master_sap_selected
from app.combat.timed_condition_lifecycle import remove_effect_instance
from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)

SAPPED_EFFECT_ID = TACTICAL_MASTER_SAP_EFFECT_ID
SOURCE_EFFECT_ID = "tactical-master"


def tactical_master_sap_eligible(
    state: CombatantState,
    attack: WeaponAttack,
) -> bool:
    try:
        return tactical_master_sap_selected(state, attack)
    except Exception:
        logger.exception(
            "Failed Tactical Master Sap eligibility for %s using %s.",
            state.template.name,
            attack.id,
        )
        raise


def apply_tactical_master_sap(
    attacker: CombatantState,
    attacker_id: str,
    target: CombatantState,
    attack: WeaponAttack,
    round_number: int,
) -> bool:
    try:
        if not tactical_master_sap_eligible(attacker, attack):
            return False
        return apply_sap_effect(
            attacker_id,
            target,
            round_number,
            effect_id=SAPPED_EFFECT_ID,
            source_effect_id=SOURCE_EFFECT_ID,
        )
    except Exception:
        logger.exception(
            "Failed to apply Tactical Master Sap from %s to %s.",
            attacker_id,
            target.template.name,
        )
        raise


def tactical_master_sap_disadvantage(state: CombatantState) -> int:
    try:
        return int(
            any(
                effect.effect_id == SAPPED_EFFECT_ID
                for effect in state.timed_effects
            )
        )
    except Exception:
        logger.exception(
            "Failed Tactical Master Sap disadvantage lookup for %s.",
            state.template.name,
        )
        raise


def consume_tactical_master_sap(state: CombatantState) -> int:
    try:
        effects = [
            effect
            for effect in list(state.timed_effects)
            if effect.effect_id == SAPPED_EFFECT_ID
        ]
        for effect in effects:
            remove_effect_instance(state, effect)
        return len(effects)
    except Exception:
        logger.exception(
            "Failed to consume Tactical Master Sap for %s.",
            state.template.name,
        )
        raise
