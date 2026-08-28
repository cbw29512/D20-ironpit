from __future__ import annotations

import logging

from app.domain.models import DamageType, VisualLoadout, Weapon, WeaponAttackKind

logger = logging.getLogger(__name__)


def build_light_crossbow() -> Weapon:
    try:
        return Weapon(
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
    except Exception as exc:
        logger.exception("Failed to build light crossbow.")
        raise RuntimeError("Light crossbow could not be created.") from exc


def build_club() -> Weapon:
    try:
        return Weapon(
            id="club",
            name="Club",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=4,
            damage_type=DamageType.BLUDGEONING,
            animation="bludgeon",
        )
    except Exception as exc:
        logger.exception("Failed to build club.")
        raise RuntimeError("Club could not be created.") from exc


def build_beak() -> Weapon:
    return Weapon(
        id="axe-beak-beak",
        name="Beak",
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=8,
        damage_type=DamageType.SLASHING,
        animation="bite",
    )


def build_giant_lizard_bite() -> Weapon:
    return Weapon(
        id="giant-lizard-bite",
        name="Bite",
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=8,
        damage_type=DamageType.PIERCING,
        animation="bite",
    )


def build_monster_visual(armor: str, main_hand: str, body_style: str) -> VisualLoadout:
    return VisualLoadout(armor=armor, main_hand=main_hand, body_style=body_style)
