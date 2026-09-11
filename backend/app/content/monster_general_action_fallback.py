from __future__ import annotations

from app.content.unarmed_opportunity_profiles import monster_unarmed_profile
from app.domain.capability_attacks import AttackCapabilityDefinition
from app.domain.weapons import DamageType, WeaponAttackKind

_GENERAL_UNARMED_SUFFIX = "-general-unarmed-strike"


def general_unarmed_attack(row: dict[str, object], definition_id: str) -> AttackCapabilityDefinition:
    """Compile the universal Unarmed Strike action for a monster with no printed attack."""
    profile = monster_unarmed_profile(row)
    attack_id = f"{definition_id}{_GENERAL_UNARMED_SUFFIX}"
    return AttackCapabilityDefinition(
        id=attack_id,
        name="Unarmed Strike",
        weapon_id=f"{attack_id}-weapon",
        attack_kind=WeaponAttackKind.MELEE,
        attack_bonus=profile.attack_bonus,
        fixed_damage=profile.damage,
        damage_type=DamageType.BLUDGEONING,
        animation="unarmed",
        reach_ft=5,
    )


def is_general_rule_attack_id(attack_id: str) -> bool:
    return attack_id.endswith(_GENERAL_UNARMED_SUFFIX)
