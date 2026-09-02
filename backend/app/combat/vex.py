from __future__ import annotations

from app.combat.modifier_stack import add_modifier
from app.domain.models import CombatantState, WeaponAttack
from app.domain.modifiers import CombatModifier, ModifierKind

VEX_EFFECT_ID = "weapon-mastery-vex"


def vex_mastery_active(attacker: CombatantState, attack: WeaponAttack) -> bool:
    return (
        attack.weapon.mastery_property == "Vex"
        and attack.weapon.id in attacker.template.weapon_masteries
    )


def apply_vex_mastery(
    attacker: CombatantState,
    attacker_id: str,
    target_id: str,
    attack: WeaponAttack,
    round_number: int,
    damage_dealt: int,
) -> bool:
    """Apply RAW Vex after a mastered weapon hits and actually deals damage."""
    if damage_dealt <= 0 or not vex_mastery_active(attacker, attack):
        return False
    add_modifier(attacker, CombatModifier(
        id=f"{attacker_id}:{VEX_EFFECT_ID}:{target_id}",
        source_id=attacker_id,
        source_effect_id=VEX_EFFECT_ID,
        kind=ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE,
        target_id=target_id,
        expires_source_turn_end_round=round_number + 1,
    ))
    return True
