from __future__ import annotations

import logging

from app.domain.models import DamageType, Weapon, WeaponAttackKind

logger = logging.getLogger(__name__)


def _build_weapon(weapon_id: str) -> Weapon:
    try:
        if weapon_id == "greatsword":
            return Weapon(
                id="greatsword",
                name="Greatsword",
                attack_kind=WeaponAttackKind.MELEE,
                dice_count=2,
                dice_size=6,
                damage_type=DamageType.SLASHING,
                animation="heavy-slash",
                reach_ft=5,
                heavy=True,
                two_handed=True,
            )
        if weapon_id == "longbow":
            return Weapon(
                id="longbow",
                name="Longbow",
                attack_kind=WeaponAttackKind.RANGED,
                dice_count=1,
                dice_size=8,
                damage_type=DamageType.PIERCING,
                animation="projectile",
                normal_range_ft=150,
                long_range_ft=600,
                projectile="arrow",
                heavy=True,
                two_handed=True,
            )
        raise ValueError(f"Unknown audited 2014 weapon: {weapon_id}.")
    except Exception:
        logger.exception("Failed to build 2014 weapon %s.", weapon_id)
        raise


def build_weapon_2014(weapon_id: str) -> Weapon:
    """Return an edition-safe 2014 weapon with no 2024 Weapon Mastery metadata."""
    try:
        return _build_weapon(weapon_id).model_copy(deep=True)
    except Exception:
        logger.exception("2014 weapon lookup failed for %s.", weapon_id)
        raise
