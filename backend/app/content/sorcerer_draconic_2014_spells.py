from __future__ import annotations

import logging

from app.domain.spells import SpellAttackAction, SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def fire_bolt_2014(attack_bonus: int, character_level: int) -> SpellAttackAction:
    try:
        if not 1 <= character_level <= 20:
            raise ValueError("2014 Fire Bolt character level must be between 1 and 20.")
        dice_count = 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)
        return SpellAttackAction(
            id="fire-bolt", name="Fire Bolt", level=0, action_cost="action",
            attack_kind="ranged", range_ft=120, attack_bonus=attack_bonus,
            damage_dice_count=dice_count, damage_dice_size=10, damage_type="fire",
            animation="spell-attack", source="D&D Basic Rules 2014: Fire Bolt",
        )
    except Exception:
        logger.exception("Failed to build 2014 Fire Bolt at level %s.", character_level)
        raise


def burning_hands_2014(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="burning-hands", name="Burning Hands", level=1, action_cost="action",
            range_ft=15,
            area=AreaTargeting(shape="cone", origin="self", length_ft=15),
            save_ability="dexterity", dc=save_dc,
            damage_dice_count=3, damage_dice_size=6, damage_type="fire",
            success_damage="half", upcast_dice_per_level=1,
            animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2014 Burning Hands.")
        raise
