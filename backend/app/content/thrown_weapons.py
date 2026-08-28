from __future__ import annotations

import logging

from app.domain.models import DamageType, Weapon, WeaponAttackKind, WeaponProperty

logger = logging.getLogger(__name__)


def build_handaxe_throw() -> Weapon:
    try:
        return Weapon(
            id="handaxe",
            name="Handaxe",
            attack_kind=WeaponAttackKind.RANGED,
            dice_count=1,
            dice_size=6,
            damage_type=DamageType.SLASHING,
            animation="projectile",
            normal_range_ft=20,
            long_range_ft=60,
            projectile="axe",
            properties=[WeaponProperty.LIGHT, WeaponProperty.THROWN],
            mastery_property="vex",
        )
    except Exception as exc:
        logger.exception("Failed to build thrown handaxe.")
        raise RuntimeError("Thrown handaxe could not be created.") from exc
