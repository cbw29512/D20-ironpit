from __future__ import annotations

import logging

from app.domain.models import DamageType, VisualLoadout, Weapon, WeaponAttackKind

logger = logging.getLogger(__name__)


def _weapon(**kwargs) -> Weapon:
    try:
        return Weapon(**kwargs)
    except Exception as exc:
        weapon_id = kwargs.get("id", "unknown")
        logger.exception("Failed to build weapon %s.", weapon_id)
        raise RuntimeError(f"Weapon {weapon_id} could not be created.") from exc


def build_light_crossbow() -> Weapon:
    return _weapon(
        id="light-crossbow",
        name="Light Crossbow",
        attack_kind=WeaponAttackKind.RANGED,
        dice_count=1,
        dice_size=8,
        damage_type=DamageType.PIERCING,
        animation="projectile",
        normal_range_ft=80,
        long_range_ft=320,
        projectile="bolt",
    )


def build_club() -> Weapon:
    return _weapon(
        id="club",
        name="Club",
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=4,
        damage_type=DamageType.BLUDGEONING,
        animation="bludgeon",
    )


def build_axe_beak_beak() -> Weapon:
    return _weapon(
        id="axe-beak-beak",
        name="Beak",
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=8,
        damage_type=DamageType.SLASHING,
        animation="bite",
    )


def build_giant_lizard_bite() -> Weapon:
    return _weapon(
        id="giant-lizard-bite",
        name="Bite",
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=8,
        damage_type=DamageType.PIERCING,
        animation="bite",
    )


def build_monster_visual(armor: str, main_hand: str, body_style: str) -> VisualLoadout:
    try:
        return VisualLoadout(armor=armor, main_hand=main_hand, body_style=body_style)
    except Exception as exc:
        logger.exception("Failed to build monster visual %s.", body_style)
        raise RuntimeError("Monster visual could not be created.") from exc
