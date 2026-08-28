from __future__ import annotations

import logging

from app.domain.models import DamageType, VisualLoadout, Weapon, WeaponAttackKind

logger = logging.getLogger(__name__)


def build_longsword() -> Weapon:
    try:
        return Weapon(
            id="longsword",
            name="Longsword",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=8,
            damage_type=DamageType.SLASHING,
            animation="slash",
            reach_ft=5,
            mastery_property="sap",
        )
    except Exception as exc:
        logger.exception("Failed to build longsword content record.")
        raise RuntimeError("Longsword content could not be created.") from exc


def build_scimitar() -> Weapon:
    try:
        return Weapon(
            id="scimitar",
            name="Scimitar",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=6,
            damage_type=DamageType.SLASHING,
            animation="slash",
            reach_ft=5,
            mastery_property="nick",
        )
    except Exception as exc:
        logger.exception("Failed to build scimitar content record.")
        raise RuntimeError("Scimitar content could not be created.") from exc


def build_shortbow() -> Weapon:
    try:
        return Weapon(
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
            mastery_property="vex",
        )
    except Exception as exc:
        logger.exception("Failed to build shortbow content record.")
        raise RuntimeError("Shortbow content could not be created.") from exc


def build_fighter_visual_loadout() -> VisualLoadout:
    try:
        return VisualLoadout(
            armor="chain-mail",
            main_hand="longsword",
            off_hand="shield",
            body_style="humanoid",
        )
    except Exception as exc:
        logger.exception("Failed to build Fighter visual loadout.")
        raise RuntimeError("Fighter visual loadout could not be created.") from exc


def build_goblin_visual_loadout() -> VisualLoadout:
    try:
        return VisualLoadout(
            armor="leather",
            main_hand="scimitar",
            off_hand="shield",
            body_style="goblinoid",
        )
    except Exception as exc:
        logger.exception("Failed to build Goblin visual loadout.")
        raise RuntimeError("Goblin visual loadout could not be created.") from exc
