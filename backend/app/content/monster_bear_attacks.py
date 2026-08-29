from __future__ import annotations

from app.domain.models import DamageType, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize


def _weapon(weapon_id: str, name: str, dice_size: int, damage_type: DamageType) -> Weapon:
    return Weapon(
        id=weapon_id,
        name=name,
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=dice_size,
        damage_type=damage_type,
        animation="bite" if name == "Bite" else "heavy-slash",
        reach_ft=5,
    )


def build_black_bear_rend() -> WeaponAttack:
    return WeaponAttack(
        id="black-bear-rend",
        weapon=_weapon("black-bear-rend-weapon", "Rend", 6, DamageType.SLASHING),
        attack_bonus=4,
        damage_bonus=2,
    )


def build_brown_bear_bite() -> WeaponAttack:
    return WeaponAttack(
        id="brown-bear-bite",
        weapon=_weapon("brown-bear-bite-weapon", "Bite", 8, DamageType.PIERCING),
        attack_bonus=5,
        damage_bonus=3,
    )


def build_brown_bear_claw() -> WeaponAttack:
    return WeaponAttack(
        id="brown-bear-claw",
        weapon=_weapon("brown-bear-claw-weapon", "Claw", 4, DamageType.SLASHING),
        attack_bonus=5,
        damage_bonus=3,
        knocks_prone_max_size=CreatureSize.LARGE,
    )
