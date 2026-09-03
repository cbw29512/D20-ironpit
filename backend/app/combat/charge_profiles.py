from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import DamageType
from app.domain.size import CreatureSize


@dataclass(frozen=True)
class ChargeDamage:
    dice_count: int
    dice_size: int
    damage_type: DamageType


@dataclass(frozen=True)
class ChargeProfile:
    attack_id: str
    minimum_move_ft: int
    max_target_size: CreatureSize
    bonus_damage: ChargeDamage | None = None
    follow_up_attack_id: str | None = None


_PROFILES = {
    "allosaurus-claws": ChargeProfile(
        "allosaurus-claws", 30, CreatureSize.LARGE, follow_up_attack_id="allosaurus-bite",
    ),
    "boar-gore": ChargeProfile(
        "boar-gore", 20, CreatureSize.MEDIUM, ChargeDamage(1, 6, DamageType.PIERCING),
    ),
    "elk-ram": ChargeProfile(
        "elk-ram", 20, CreatureSize.LARGE, ChargeDamage(1, 6, DamageType.BLUDGEONING),
    ),
    "giant-boar-gore": ChargeProfile(
        "giant-boar-gore", 20, CreatureSize.LARGE, ChargeDamage(2, 6, DamageType.PIERCING),
    ),
    "giant-elk-ram": ChargeProfile(
        "giant-elk-ram", 20, CreatureSize.HUGE, ChargeDamage(2, 4, DamageType.BLUDGEONING),
    ),
    "giant-goat-ram": ChargeProfile(
        "giant-goat-ram", 20, CreatureSize.LARGE, ChargeDamage(2, 4, DamageType.BLUDGEONING),
    ),
    "minotaur-skeleton-gore": ChargeProfile(
        "minotaur-skeleton-gore", 20, CreatureSize.LARGE, ChargeDamage(2, 8, DamageType.PIERCING),
    ),
    "rhinoceros-gore": ChargeProfile(
        "rhinoceros-gore", 20, CreatureSize.LARGE, ChargeDamage(2, 8, DamageType.PIERCING),
    ),
    "triceratops-gore": ChargeProfile(
        "triceratops-gore", 20, CreatureSize.HUGE, ChargeDamage(2, 8, DamageType.PIERCING),
    ),
    "warhorse-hooves": ChargeProfile(
        "warhorse-hooves", 20, CreatureSize.LARGE, ChargeDamage(2, 4, DamageType.BLUDGEONING),
    ),
    "warhorse-skeleton-hooves": ChargeProfile(
        "warhorse-skeleton-hooves", 20, CreatureSize.LARGE,
    ),
}


def charge_profile_for_attack_id(attack_id: str) -> ChargeProfile | None:
    return _PROFILES.get(attack_id)
