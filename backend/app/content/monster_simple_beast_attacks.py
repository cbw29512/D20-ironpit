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
            animation="bite" if name == "Bite" else "heavy-strike",
            reach_ft=5,
        ),
        attack_bonus=attack_bonus,
        damage_bonus=damage_bonus,
    )


def build_baboon_bite() -> WeaponAttack:
    return _attack("baboon-bite", "Bite", 1, 1, 4, -1, DamageType.PIERCING)


def build_camel_bite() -> WeaponAttack:
    return _attack("camel-bite", "Bite", 4, 1, 4, 2, DamageType.BLUDGEONING)


def build_deer_ram() -> WeaponAttack:
    return _attack("deer-ram", "Ram", 2, 1, 4, 0, DamageType.BLUDGEONING)


def build_draft_horse_hooves() -> WeaponAttack:
    return _attack("draft-horse-hooves", "Hooves", 6, 1, 4, 4, DamageType.BLUDGEONING)


def build_giant_badger_bite() -> WeaponAttack:
    return _attack("giant-badger-bite", "Bite", 3, 2, 4, 1, DamageType.PIERCING)


def build_jackal_bite() -> WeaponAttack:
    return _attack("jackal-bite", "Bite", 1, 1, 4, -1, DamageType.PIERCING)
