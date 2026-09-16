from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import DamageType
from app.domain.size import CreatureSize
from app.domain.weapons import WeaponAttack


@dataclass(frozen=True)
class ChargeDamage:
    dice_count: int
    dice_size: int
    damage_type: DamageType
    damage_bonus: int = 0


@dataclass(frozen=True)
class ChargeProfile:
    attack_id: str
    minimum_move_ft: int
    max_target_size: CreatureSize | None = None
    prone_max_target_size: CreatureSize | None = None
    prone_save_ability: str | None = None
    prone_save_dc: int | None = None
    bonus_damage: ChargeDamage | None = None
    replacement_damage: ChargeDamage | None = None
    follow_up_attack_id: str | None = None
    follow_up_required_target_condition: str | None = None
    follow_up_action_cost: str = "free"


def _prone_charge(
    attack_id: str, minimum_move_ft: int, maximum: CreatureSize, *,
    bonus_damage: ChargeDamage | None = None, follow_up_attack_id: str | None = None,
) -> ChargeProfile:
    return ChargeProfile(
        attack_id, minimum_move_ft, max_target_size=maximum, prone_max_target_size=maximum,
        bonus_damage=bonus_damage, follow_up_attack_id=follow_up_attack_id,
    )


_PROFILES = {
    "allosaurus-claws": _prone_charge(
        "allosaurus-claws", 30, CreatureSize.LARGE, follow_up_attack_id="allosaurus-bite",
    ),
    "boar-gore": _prone_charge(
        "boar-gore", 20, CreatureSize.MEDIUM, bonus_damage=ChargeDamage(1, 6, DamageType.PIERCING),
    ),
    "elk-ram": _prone_charge(
        "elk-ram", 20, CreatureSize.LARGE, bonus_damage=ChargeDamage(1, 6, DamageType.BLUDGEONING),
    ),
    "giant-boar-gore": _prone_charge(
        "giant-boar-gore", 20, CreatureSize.LARGE, bonus_damage=ChargeDamage(2, 6, DamageType.PIERCING),
    ),
    "giant-elk-ram": _prone_charge(
        "giant-elk-ram", 20, CreatureSize.HUGE, bonus_damage=ChargeDamage(2, 4, DamageType.BLUDGEONING),
    ),
    "giant-goat-ram": _prone_charge(
        "giant-goat-ram", 20, CreatureSize.LARGE, bonus_damage=ChargeDamage(2, 4, DamageType.BLUDGEONING),
    ),
    "goat-ram": ChargeProfile(
        "goat-ram", 20, replacement_damage=ChargeDamage(1, 4, DamageType.BLUDGEONING),
    ),
    "minotaur-skeleton-gore": _prone_charge(
        "minotaur-skeleton-gore", 20, CreatureSize.LARGE, bonus_damage=ChargeDamage(2, 8, DamageType.PIERCING),
    ),
    "rhinoceros-gore": _prone_charge(
        "rhinoceros-gore", 20, CreatureSize.LARGE, bonus_damage=ChargeDamage(2, 8, DamageType.PIERCING),
    ),
    "triceratops-gore": _prone_charge(
        "triceratops-gore", 20, CreatureSize.HUGE, bonus_damage=ChargeDamage(2, 8, DamageType.PIERCING),
    ),
    "warhorse-hooves": _prone_charge(
        "warhorse-hooves", 20, CreatureSize.LARGE, bonus_damage=ChargeDamage(2, 4, DamageType.BLUDGEONING),
    ),
    "warhorse-skeleton-hooves": _prone_charge(
        "warhorse-skeleton-hooves", 20, CreatureSize.LARGE,
    ),
}


def charge_profile_for_attack_id(attack_id: str) -> ChargeProfile | None:
    return _PROFILES.get(attack_id)


def charge_profile_for_attack(attack: WeaponAttack) -> ChargeProfile | None:
    declared = attack.charge_profile
    if declared is None:
        return charge_profile_for_attack_id(attack.id)
    def damage(value):
        if value is None:
            return None
        return ChargeDamage(value.dice_count, value.dice_size, value.damage_type, value.damage_bonus)
    return ChargeProfile(
        attack_id=attack.id,
        minimum_move_ft=declared.minimum_move_ft,
        max_target_size=declared.max_target_size,
        prone_max_target_size=declared.prone_max_target_size,
        prone_save_ability=declared.prone_save_ability,
        prone_save_dc=declared.prone_save_dc,
        bonus_damage=damage(declared.bonus_damage),
        replacement_damage=damage(declared.replacement_damage),
        follow_up_attack_id=declared.follow_up_attack_id,
        follow_up_required_target_condition=declared.follow_up_required_target_condition,
        follow_up_action_cost=declared.follow_up_action_cost,
    )
