from __future__ import annotations

import logging

from app.domain.spells import SpellAttackAction, SpellModifierEffect, SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def fire_bolt_2014(attack_bonus: int, character_level: int, damage_bonus: int = 0) -> SpellAttackAction:
    try:
        if not 1 <= character_level <= 20:
            raise ValueError("2014 Fire Bolt character level must be between 1 and 20.")
        dice_count = 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)
        return SpellAttackAction(
            id="fire-bolt", name="Fire Bolt", level=0, action_cost="action",
            attack_kind="ranged", range_ft=120, attack_bonus=attack_bonus,
            damage_dice_count=dice_count, damage_dice_size=10, damage_bonus=damage_bonus, damage_type="fire",
            animation="spell-attack", source="D&D Basic Rules 2014: Fire Bolt",
        )
    except Exception:
        logger.exception("Failed to build 2014 Fire Bolt at level %s.", character_level)
        raise


def burning_hands_2014(save_dc: int, damage_bonus: int = 0) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="burning-hands", name="Burning Hands", level=1, action_cost="action",
            range_ft=15,
            area=AreaTargeting(shape="cone", origin="self", length_ft=15),
            save_ability="dexterity", dc=save_dc,
            damage_dice_count=3, damage_dice_size=6, damage_bonus=damage_bonus, damage_type="fire",
            success_damage="half", upcast_dice_per_level=1,
            animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2014 Burning Hands.")
        raise


def fireball_2014(save_dc: int, damage_bonus: int = 0) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="fireball", name="Fireball", level=3, action_cost="action",
            range_ft=150,
            area=AreaTargeting(shape="radius", origin="point", radius_ft=20),
            save_ability="dexterity", dc=save_dc,
            damage_dice_count=8, damage_dice_size=6, damage_bonus=damage_bonus, damage_type="fire",
            success_damage="half", upcast_dice_per_level=1,
            animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2014 Fireball.")
        raise


def ray_of_frost_2014(attack_bonus: int, character_level: int) -> SpellAttackAction:
    try:
        dice_count = 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)
        return SpellAttackAction(
            id="ray-of-frost", name="Ray of Frost", level=0, action_cost="action",
            attack_kind="ranged", range_ft=60, attack_bonus=attack_bonus,
            damage_dice_count=dice_count, damage_dice_size=8, damage_type="cold",
            on_hit_modifier_effects=[
                SpellModifierEffect(kind="speed", flat_bonus=-10, expires_after_source_turns=1),
            ],
            animation="spell-attack", source="D&D Basic Rules 2014: Ray of Frost",
        )
    except Exception:
        logger.exception("Failed to build 2014 Ray of Frost.")
        raise


def poison_spray_2014(save_dc: int, character_level: int) -> SpellSaveAction:
    try:
        dice_count = 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)
        return SpellSaveAction(
            id="poison-spray", name="Poison Spray", level=0, action_cost="action",
            range_ft=10, save_ability="constitution", dc=save_dc,
            damage_dice_count=dice_count, damage_dice_size=12, damage_type="poison",
            success_damage="none", animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2014 Poison Spray.")
        raise


def shatter_2014(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="shatter", name="Shatter", level=2, action_cost="action",
            range_ft=60,
            area=AreaTargeting(shape="radius", origin="point", radius_ft=10),
            save_ability="constitution", dc=save_dc,
            damage_dice_count=3, damage_dice_size=8, damage_type="thunder",
            success_damage="half", upcast_dice_per_level=1, animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2014 Shatter.")
        raise


def lightning_bolt_2014(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="lightning-bolt", name="Lightning Bolt", level=3, action_cost="action",
            range_ft=100,
            area=AreaTargeting(shape="line", origin="self", length_ft=100, width_ft=5),
            save_ability="dexterity", dc=save_dc,
            damage_dice_count=8, damage_dice_size=6, damage_type="lightning",
            success_damage="half", upcast_dice_per_level=1, animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2014 Lightning Bolt.")
        raise


def cone_of_cold_2014(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="cone-of-cold", name="Cone of Cold", level=5, action_cost="action",
            range_ft=60,
            area=AreaTargeting(shape="cone", origin="self", length_ft=60),
            save_ability="constitution", dc=save_dc,
            damage_dice_count=8, damage_dice_size=8, damage_type="cold",
            success_damage="half", upcast_dice_per_level=1, animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2014 Cone of Cold.")
        raise
