from __future__ import annotations

from app.domain.models import DamageType, Weapon, WeaponAttack, WeaponAttackKind


def _attack(
    attack_id: str,
    name: str,
    attack_bonus: int,
    dice_count: int,
    dice_size: int,
    damage_bonus: int,
    damage_type: DamageType,
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
    )


def build_boar_gore() -> WeaponAttack:
    return _attack("boar-gore", "Gore", 3, 1, 6, 1, DamageType.PIERCING)


def build_elk_ram() -> WeaponAttack:
    return _attack("elk-ram", "Ram", 5, 1, 6, 3, DamageType.BLUDGEONING)


def build_giant_boar_gore() -> WeaponAttack:
    return _attack("giant-boar-gore", "Gore", 5, 2, 6, 3, DamageType.PIERCING)
