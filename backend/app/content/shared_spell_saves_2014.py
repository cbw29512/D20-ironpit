from __future__ import annotations

import logging

from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)
_SOURCE = "D&D Basic Rules 2014 / SRD 5.1"


def _cantrip_dice(character_level: int) -> int:
    try:
        if character_level not in range(1, 21):
            raise ValueError("Cantrip character level must be between 1 and 20.")
        return 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)
    except Exception:
        logger.exception("Failed to resolve 2014 save-cantrip scaling at level %s.", character_level)
        raise


def poison_spray_2014(save_dc: int, character_level: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="poison-spray", name="Poison Spray", level=0, action_cost="action",
            range_ft=10, save_ability="constitution", dc=save_dc,
            damage_dice_count=_cantrip_dice(character_level), damage_dice_size=12,
            damage_type="poison", success_damage="none", animation="poison-spray",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Poison Spray at character level %s.", character_level)
        raise


def shatter_2014(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="shatter", name="Shatter", level=2, action_cost="action",
            range_ft=60, area_radius_ft=10, save_ability="constitution", dc=save_dc,
            damage_dice_count=3, damage_dice_size=8, damage_type="thunder",
            success_damage="half", animation="shatter",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Shatter.")
        raise


def fireball_2014(save_dc: int, slot_level: int = 3) -> SpellSaveAction:
    try:
        if slot_level not in range(3, 10):
            raise ValueError("2014 Fireball slot level must be between 3 and 9.")
        return SpellSaveAction(
            id="fireball" if slot_level == 3 else f"fireball-l{slot_level}",
            name="Fireball" if slot_level == 3 else f"Fireball ({slot_level}th-Level)",
            level=slot_level, action_cost="action", range_ft=150, area_radius_ft=20,
            save_ability="dexterity", dc=save_dc,
            damage_dice_count=8 + (slot_level - 3), damage_dice_size=6,
            damage_type="fire", success_damage="half", upcast_dice_per_level=1,
            animation="fireball",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Fireball at slot level %s.", slot_level)
        raise


def disintegrate_2014(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="disintegrate", name="Disintegrate", level=6, action_cost="action",
            range_ft=60, save_ability="dexterity", dc=save_dc,
            damage_dice_count=10, damage_dice_size=6, damage_bonus=40,
            damage_type="force", success_damage="none", animation="disintegrate",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Disintegrate.")
        raise
