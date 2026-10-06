"""Pure printed-damage values for legal Action candidate ranking, never applied damage."""
from __future__ import annotations

import logging

from app.domain.models import WeaponAttack

logger = logging.getLogger(__name__)


def weapon_mean_damage(attack: WeaponAttack) -> float:
    try:
        return attack.weapon.dice_count * (attack.weapon.dice_size + 1) / 2 + attack.damage_bonus
    except Exception:
        logger.exception("Failed printed weapon damage for %s.", attack.id)
        raise


def save_mean_damage(action) -> float:
    try:
        parts = action.damage_components or (
            [action] if getattr(action, "damage_dice_count", 0) else []
        )
        total = 0.0
        for part in parts:
            count = getattr(part, "dice_count", getattr(part, "damage_dice_count", 0))
            size = getattr(part, "dice_size", getattr(part, "damage_dice_size", 0))
            bonus = getattr(part, "damage_bonus", 0)
            if count:
                total += count * (size + 1) / 2 + bonus
        return total
    except Exception:
        logger.exception("Failed printed save-action damage for %s.", getattr(action, "id", "?"))
        raise
