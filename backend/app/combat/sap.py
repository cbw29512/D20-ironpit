from __future__ import annotations

from app.combat.modifier_stack import (
    add_modifier,
    consume_next_attack_disadvantage,
    next_attack_disadvantage_sources,
)
from app.combat.weapon_mastery import weapon_mastery_active
from app.domain.models import CombatantState, WeaponAttack
from app.domain.modifiers import CombatModifier, ModifierKind

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
    del round_number, source_effect_id
    if target.is_dead or target.current_hp <= 0:
        return False
    before = next_attack_disadvantage_sources(target)
    add_modifier(target, CombatModifier(
        id=f"{attacker_id}:{effect_id}",
        source_id=attacker_id,
        source_effect_id=effect_id,
        kind=ModifierKind.NEXT_ATTACK_DISADVANTAGE,
        expires_at_start_of_source_turn=True,
    ))
    return next_attack_disadvantage_sources(target) > before


def weapon_sap_eligible(state: CombatantState, attack: WeaponAttack) -> bool:
    return weapon_mastery_active(state, attack, "Sap")


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
    """Compatibility alias; the actual math is the universal modifier stack."""
    return next_attack_disadvantage_sources(state)


def consume_sap(state: CombatantState) -> int:
    """Compatibility alias; next-attack disadvantage consumes on the next attack roll."""
    return consume_next_attack_disadvantage(state)
