from __future__ import annotations

from app.combat.timed_conditions import apply_timed_condition, remove_effect_instance
from app.domain.models import CombatantState, WeaponAttack

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


def weapon_sap_eligible(state: CombatantState, attack: WeaponAttack) -> bool:
    return (
        attack.weapon.mastery_property == "Sap"
        and attack.weapon.id in state.template.weapon_masteries
    )


def apply_weapon_sap(
    attacker: CombatantState,
    attacker_id: str,
    target: CombatantState,
    attack: WeaponAttack,
    round_number: int,
) -> bool:
    if not weapon_sap_eligible(attacker, attack):
        return False
    return apply_sap_effect(
        attacker_id,
        target,
        round_number,
        effect_id=WEAPON_SAP_EFFECT_ID,
        source_effect_id="weapon-mastery",
    )


def sap_disadvantage(state: CombatantState) -> int:
    return int(any(effect.effect_id in SAP_EFFECT_IDS for effect in state.timed_effects))


def consume_sap(state: CombatantState) -> int:
    effects = [effect for effect in list(state.timed_effects) if effect.effect_id in SAP_EFFECT_IDS]
    for effect in effects:
        remove_effect_instance(state, effect)
    return len(effects)
