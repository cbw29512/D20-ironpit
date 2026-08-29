from __future__ import annotations

from app.domain.models import DamageType, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize


def _bite(
    attack_id: str,
    attack_bonus: int,
    dice_size: int,
    damage_bonus: int,
    prone_max_size: CreatureSize,
) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id,
            name="Bite",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=dice_size,
            damage_type=DamageType.PIERCING,
            animation="bite",
            reach_ft=5,
        ),
        attack_bonus=attack_bonus,
        damage_bonus=damage_bonus,
        knocks_prone_max_size=prone_max_size,
    )


def build_wolf_bite() -> WeaponAttack:
    return _bite("wolf-bite", 4, 6, 2, CreatureSize.MEDIUM)


def build_dire_wolf_bite() -> WeaponAttack:
    return _bite("dire-wolf-bite", 5, 10, 3, CreatureSize.LARGE)
