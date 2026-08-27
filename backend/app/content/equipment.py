from __future__ import annotations

import logging

from app.domain.models import (
    ConditionalDamage,
    DamageType,
    VisualLoadout,
    Weapon,
    WeaponAttackKind,
)

logger = logging.getLogger(__name__)


def build_longsword() -> Weapon:
    try:
        return Weapon(
            id="longsword",
            name="Longsword",
            attack_kind=WeaponAttackKind.MELEE,
            attack_bonus=5,
            dice_count=1,
            dice_size=8,
            damage_bonus=3,
            damage_type=DamageType.SLASHING,
            animation="slash",
            reach_ft=5,
        )
    except Exception as exc:
        logger.exception("Failed to build longsword content record.")
        raise RuntimeError("Longsword content could not be created.") from exc


def _goblin_advantage_damage(damage_type: DamageType) -> list[ConditionalDamage]:
    try:
        return [
            ConditionalDamage(
                trigger="attack_advantage",
                dice_count=1,
                dice_size=4,
                damage_type=damage_type,
            )
        ]
    except Exception as exc:
        logger.exception("Failed to build Goblin advantage damage.")
        raise RuntimeError("Goblin conditional damage could not be created.") from exc


def build_scimitar() -> Weapon:
    try:
        return Weapon(
            id="scimitar",
            name="Scimitar",
            attack_kind=WeaponAttackKind.MELEE,
            attack_bonus=4,
            dice_count=1,
            dice_size=6,
            damage_bonus=2,
            damage_type=DamageType.SLASHING,
            animation="slash",
            reach_ft=5,
            conditional_damage=_goblin_advantage_damage(DamageType.SLASHING),
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
            attack_bonus=4,
            dice_count=1,
            dice_size=6,
            damage_bonus=2,
            damage_type=DamageType.PIERCING,
            animation="projectile",
            normal_range_ft=80,
            long_range_ft=320,
            projectile="arrow",
            conditional_damage=_goblin_advantage_damage(DamageType.PIERCING),
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
