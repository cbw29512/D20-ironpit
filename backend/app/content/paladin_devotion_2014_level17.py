from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.domain.save_damage import SaveDamageComponent
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def flame_strike_2014(level: int, charisma_modifier: int) -> SpellSaveAction:
    try:
        if level < 17:
            raise ValueError("2014 Flame Strike requires Paladin level 17.")
        return SpellSaveAction(
            id="flame-strike",
            name="Flame Strike",
            level=5,
            action_cost="action",
            range_ft=60,
            area_radius_ft=10,
            save_ability="dexterity",
            dc=8 + proficiency_bonus(level) + charisma_modifier,
            success_damage="half",
            damage_components=[
                SaveDamageComponent(dice_count=4, dice_size=6, damage_type="fire"),
                SaveDamageComponent(dice_count=4, dice_size=6, damage_type="radiant"),
            ],
            animation="flame-strike",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Flame Strike at Paladin level %s.", level)
        raise
