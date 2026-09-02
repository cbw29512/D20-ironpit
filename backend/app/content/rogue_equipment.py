from __future__ import annotations

import logging

from app.domain.models import DamageType, VisualLoadout, Weapon, WeaponAttackKind

logger = logging.getLogger(__name__)


def _weapon(**kwargs) -> Weapon:
    try:
        return Weapon(**kwargs)
    except Exception as exc:
        weapon_id = kwargs.get("id", "unknown")
        logger.exception("Failed to build Rogue weapon %s.", weapon_id)
        raise RuntimeError(f"Rogue weapon {weapon_id} could not be created.") from exc


def build_shortsword() -> Weapon:
    return _weapon(
        id="shortsword",
        name="Shortsword",
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=6,
        damage_type=DamageType.PIERCING,
        animation="thrust",
        mastery_property="Vex",
        light=True,
    )


def build_shortbow() -> Weapon:
    return _weapon(
        id="shortbow",
        name="Shortbow",
        attack_kind=WeaponAttackKind.RANGED,
        dice_count=1,
        dice_size=6,
        damage_type=DamageType.PIERCING,
        animation="projectile",
        normal_range_ft=80,
        long_range_ft=320,
        projectile="arrow",
        mastery_property="Vex",
    )


def build_rogue_visual_loadout() -> VisualLoadout:
    try:
        return VisualLoadout(
            armor="leather",
            main_hand="shortsword",
            off_hand="shortbow",
            body_style="rogue",
        )
    except Exception as exc:
        logger.exception("Failed to build Rogue visual loadout.")
        raise RuntimeError("Rogue visual loadout could not be created.") from exc
