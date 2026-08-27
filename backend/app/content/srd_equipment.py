from __future__ import annotations

import logging

from app.domain.models import DamageType, Weapon, WeaponAttackKind

logger = logging.getLogger(__name__)


def build_shortsword() -> Weapon:
    try:
        return Weapon(
            id="shortsword",
            name="Shortsword",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=6,
            damage_type=DamageType.PIERCING,
            animation="slash",
            reach_ft=5,
            mastery_property="vex",
        )
    except Exception as exc:
        logger.exception("Failed to build shortsword content record.")
        raise RuntimeError("Shortsword content could not be created.") from exc


def build_greatclub() -> Weapon:
    try:
        return Weapon(
            id="greatclub",
            name="Greatclub",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=8,
            damage_type=DamageType.BLUDGEONING,
            animation="smash",
            reach_ft=5,
            mastery_property="push",
        )
    except Exception as exc:
        logger.exception("Failed to build greatclub content record.")
        raise RuntimeError("Greatclub content could not be created.") from exc


def build_javelin() -> Weapon:
    try:
        return Weapon(
            id="javelin",
            name="Javelin",
            attack_kind=WeaponAttackKind.THROWN,
            dice_count=1,
            dice_size=6,
            damage_type=DamageType.PIERCING,
            animation="projectile",
            reach_ft=5,
            normal_range_ft=30,
            long_range_ft=120,
            projectile="javelin",
            mastery_property="slow",
        )
    except Exception as exc:
        logger.exception("Failed to build javelin content record.")
        raise RuntimeError("Javelin content could not be created.") from exc
