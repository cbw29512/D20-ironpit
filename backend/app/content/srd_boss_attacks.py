from __future__ import annotations

import logging

from app.content.srd_equipment import build_heavy_crossbow, build_warhammer
from app.domain.models import DamageDiceOverride, WeaponAttack

logger = logging.getLogger(__name__)


def build_tough_boss_warhammer_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="tough-boss-warhammer",
            weapon=build_warhammer(),
            attack_bonus=5,
            damage_bonus=3,
            damage_dice=DamageDiceOverride(dice_count=2, dice_size=8),
        )
    except Exception as exc:
        logger.exception("Failed to build Tough Boss warhammer attack.")
        raise RuntimeError("Tough Boss warhammer attack could not be created.") from exc


def build_tough_boss_crossbow_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="tough-boss-heavy-crossbow",
            weapon=build_heavy_crossbow(),
            attack_bonus=4,
            damage_bonus=2,
            damage_dice=DamageDiceOverride(dice_count=2, dice_size=10),
        )
    except Exception as exc:
        logger.exception("Failed to build Tough Boss Heavy Crossbow attack.")
        raise RuntimeError("Tough Boss Heavy Crossbow attack could not be created.") from exc
