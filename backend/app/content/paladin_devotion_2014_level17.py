from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.shared_damage_spells_2014 import (
    flame_strike_2014 as shared_flame_strike_2014,
)
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def flame_strike_2014(level: int, charisma_modifier: int) -> SpellSaveAction:
    try:
        if level < 17:
            raise ValueError("2014 Flame Strike requires Paladin level 17.")
        return shared_flame_strike_2014(
            8 + proficiency_bonus(level) + charisma_modifier,
        )
    except Exception:
        logger.exception("Failed to compile 2014 Flame Strike at Paladin level %s.", level)
        raise
