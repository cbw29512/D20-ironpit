from __future__ import annotations

from app.domain.models import ChargeDamage, ChargeDefinition, DamageType, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize


def _attack(
    attack_id: str,
    name: str,
    attack_bonus: int,
    dice_count: int,
    dice_size: int,
    damage_bonus: int,
    damage_type: DamageType,
    charge: ChargeDefinition,
) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=f"{attack_id}-weapon",
            name=name,
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=dice_count,
            dice_size=dice_size,
            damage_type=damage_type,
            animation="heavy-strike",
            reach_ft=5,
        ),
        attack_bonus=attack_bonus,
        damage_bonus=damage_bonus,
        charge=charge,
    )


def _prone_bonus(minimum: int, maximum: CreatureSize, count: int, size: int, damage_type: DamageType) -> ChargeDefinition:
    return ChargeDefinition(
        minimum_move_ft=minimum, max_target_size=maximum, prone_max_target_size=maximum,
        bonus_damage=ChargeDamage(dice_count=count, dice_size=size, damage_type=damage_type),
    )


def build_boar_gore() -> WeaponAttack:
    return _attack(
        "boar-gore", "Gore", 3, 1, 6, 1, DamageType.PIERCING,
        _prone_bonus(20, CreatureSize.MEDIUM, 1, 6, DamageType.PIERCING),
    )


def build_elk_ram() -> WeaponAttack:
    return _attack(
        "elk-ram", "Ram", 5, 1, 6, 3, DamageType.BLUDGEONING,
        _prone_bonus(20, CreatureSize.LARGE, 1, 6, DamageType.BLUDGEONING),
    )


def build_giant_boar_gore() -> WeaponAttack:
    return _attack(
        "giant-boar-gore", "Gore", 5, 2, 6, 3, DamageType.PIERCING,
        _prone_bonus(20, CreatureSize.LARGE, 2, 6, DamageType.PIERCING),
    )
