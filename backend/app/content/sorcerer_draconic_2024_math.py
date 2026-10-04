from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points

logger = logging.getLogger(__name__)


def nyra_2024_hit_points(level: int, constitution_modifier: int) -> int:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Draconic Resilience HP currently covers levels 1 through 20.")
        bonus = level if level >= 3 else 0
        return fixed_hit_points(level, 6, constitution_modifier) + bonus
    except Exception:
        logger.exception("Failed to compile 2024 Nyra hit points at level %s.", level)
        raise


def nyra_2024_armor_class(level: int, dexterity_modifier: int, charisma_modifier: int) -> int:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Draconic Resilience AC currently covers levels 1 through 20.")
        if level >= 3:
            return 10 + dexterity_modifier + charisma_modifier
        return 10 + dexterity_modifier
    except Exception:
        logger.exception("Failed to compile 2024 Nyra armor class at level %s.", level)
        raise
