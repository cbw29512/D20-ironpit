from __future__ import annotations

import logging

from app.content.equipment import build_shortbow
from app.content.srd_equipment import (
    build_greatclub,
    build_greatsword,
    build_heavy_crossbow,
    build_javelin,
    build_shortsword,
)
from app.domain.models import ConditionalDamage, DamageDiceOverride, DamageType, WeaponAttack

logger = logging.getLogger(__name__)


def build_skeleton_shortsword_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="skeleton-shortsword",
            weapon=build_shortsword(),
            attack_bonus=5,
            damage_bonus=3,
        )
    except Exception as exc:
        logger.exception("Failed to build Skeleton shortsword attack.")
        raise RuntimeError("Skeleton shortsword attack could not be created.") from exc


def build_skeleton_shortbow_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="skeleton-shortbow",
            weapon=build_shortbow(),
            attack_bonus=5,
            damage_bonus=3,
        )
    except Exception as exc:
        logger.exception("Failed to build Skeleton shortbow attack.")
        raise RuntimeError("Skeleton shortbow attack could not be created.") from exc


def build_ogre_greatclub_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="ogre-greatclub",
            weapon=build_greatclub(),
            attack_bonus=6,
            damage_bonus=4,
            damage_dice=DamageDiceOverride(dice_count=2, dice_size=8),
        )
    except Exception as exc:
        logger.exception("Failed to build Ogre greatclub attack.")
        raise RuntimeError("Ogre greatclub attack could not be created.") from exc


def build_ogre_javelin_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="ogre-javelin",
            weapon=build_javelin(),
            attack_bonus=6,
            damage_bonus=4,
            damage_dice=DamageDiceOverride(dice_count=2, dice_size=6),
        )
    except Exception as exc:
        logger.exception("Failed to build Ogre javelin attack.")
        raise RuntimeError("Ogre javelin attack could not be created.") from exc


def _knight_radiant_rider() -> list[ConditionalDamage]:
    return [
        ConditionalDamage(
            trigger="always",
            dice_count=1,
            dice_size=8,
            damage_type=DamageType.RADIANT,
        )
    ]


def build_knight_greatsword_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="knight-greatsword",
            weapon=build_greatsword(),
            attack_bonus=5,
            damage_bonus=3,
            conditional_damage=_knight_radiant_rider(),
        )
    except Exception as exc:
        logger.exception("Failed to build Knight greatsword attack.")
        raise RuntimeError("Knight greatsword attack could not be created.") from exc


def build_knight_crossbow_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="knight-heavy-crossbow",
            weapon=build_heavy_crossbow(),
            attack_bonus=2,
            damage_bonus=0,
            damage_dice=DamageDiceOverride(dice_count=2, dice_size=10),
            conditional_damage=_knight_radiant_rider(),
        )
    except Exception as exc:
        logger.exception("Failed to build Knight Heavy Crossbow attack.")
        raise RuntimeError("Knight Heavy Crossbow attack could not be created.") from exc
