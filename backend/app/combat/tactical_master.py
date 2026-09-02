from __future__ import annotations

from app.combat.sap import TACTICAL_MASTER_SAP_EFFECT_ID, apply_sap_effect
from app.combat.timed_conditions import remove_effect_instance
from app.domain.models import CombatantState, WeaponAttack

SAPPED_EFFECT_ID = TACTICAL_MASTER_SAP_EFFECT_ID
SOURCE_EFFECT_ID = "tactical-master"


def tactical_master_sap_eligible(state: CombatantState, attack: WeaponAttack) -> bool:
    return (
        state.template.progression_features.tactical_master_sap
        and attack.weapon.id in state.template.weapon_masteries
    )


def apply_tactical_master_sap(
    attacker: CombatantState,
    attacker_id: str,
    target: CombatantState,
    attack: WeaponAttack,
    round_number: int,
) -> bool:
    if not tactical_master_sap_eligible(attacker, attack):
        return False
    return apply_sap_effect(
        attacker_id,
        target,
        round_number,
        effect_id=SAPPED_EFFECT_ID,
        source_effect_id=SOURCE_EFFECT_ID,
    )


def tactical_master_sap_disadvantage(state: CombatantState) -> int:
    return int(any(effect.effect_id == SAPPED_EFFECT_ID for effect in state.timed_effects))


def consume_tactical_master_sap(state: CombatantState) -> int:
    effects = [effect for effect in list(state.timed_effects) if effect.effect_id == SAPPED_EFFECT_ID]
    for effect in effects:
        remove_effect_instance(state, effect)
    return len(effects)
