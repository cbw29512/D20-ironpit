from __future__ import annotations

import logging

from app.domain.save_damage import SaveDamageComponent
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def flame_strike_2014(save_dc: int) -> SpellSaveAction:
    """Build source-neutral 2014 Flame Strike with independent damage components."""
    try:
        return SpellSaveAction(
            id="flame-strike",
            name="Flame Strike",
            level=5,
            action_cost="action",
            range_ft=60,
            area_radius_ft=10,
            save_ability="dexterity",
            dc=save_dc,
            success_damage="half",
            damage_components=[
                SaveDamageComponent(
                    dice_count=4, dice_size=6, damage_type="fire", upcast_dice_per_level=1,
                ),
                SaveDamageComponent(dice_count=4, dice_size=6, damage_type="radiant"),
            ],
            animation="flame-strike",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Flame Strike.")
        raise


def harm_2014(save_dc: int) -> SpellSaveAction:
    """Build 2014 Harm: 14d6 necrotic, Constitution half, floor 1 HP, failed-save max-HP loss."""
    try:
        return SpellSaveAction(
            id="harm",
            name="Harm",
            level=6,
            action_cost="action",
            range_ft=60,
            save_ability="constitution",
            dc=save_dc,
            damage_dice_count=14,
            damage_dice_size=6,
            damage_type="necrotic",
            success_damage="half",
            requires_target_sight=True,
            excluded_target_creature_types=["undead", "construct"],
            minimum_remaining_hp=1,
            reduce_hit_point_maximum_on_failed_save=True,
            animation="harm",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Harm.")
        raise


def disintegrate_2014(save_dc: int) -> SpellSaveAction:
    """Build 2014 Disintegrate: 10d6+40 force, Constitution, no damage on success."""
    try:
        return SpellSaveAction(
            id="disintegrate", name="Disintegrate", level=6, action_cost="action",
            range_ft=60, save_ability="constitution", dc=save_dc,
            damage_dice_count=10, damage_dice_size=6, damage_bonus=40, damage_type="force",
            success_damage="none", animation="disintegrate",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Disintegrate.")
        raise


def finger_of_death_2014(save_dc: int) -> SpellSaveAction:
    """Build 2014 Finger of Death: 7d8+30 necrotic, Constitution half."""
    try:
        return SpellSaveAction(
            id="finger-of-death", name="Finger of Death", level=7, action_cost="action",
            range_ft=60, save_ability="constitution", dc=save_dc,
            damage_dice_count=7, damage_dice_size=8, damage_bonus=30, damage_type="necrotic",
            success_damage="half", animation="finger-of-death",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Finger of Death.")
        raise


def blight_2014(save_dc: int) -> SpellSaveAction:
    """Build 2014 Blight: 8d8 necrotic, Constitution half."""
    try:
        return SpellSaveAction(
            id="blight", name="Blight", level=4, action_cost="action",
            range_ft=30, save_ability="constitution", dc=save_dc,
            damage_dice_count=8, damage_dice_size=8, damage_type="necrotic",
            success_damage="half", animation="blight",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Blight.")
        raise


def cloudkill_2014(save_dc: int) -> SpellSaveAction:
    """Build 2014 Cloudkill: 5d8 poison, Constitution half."""
    try:
        return SpellSaveAction(
            id="cloudkill", name="Cloudkill", level=5, action_cost="action",
            range_ft=120, save_ability="constitution", dc=save_dc,
            damage_dice_count=5, damage_dice_size=8, damage_type="poison",
            success_damage="half", animation="cloudkill",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Cloudkill.")
        raise


def ice_storm_2014(save_dc: int) -> SpellSaveAction:
    """Build 2014 Ice Storm: 2d8 bludgeoning + 4d6 cold, Dexterity half."""
    try:
        return SpellSaveAction(
            id="ice-storm", name="Ice Storm", level=4, action_cost="action",
            range_ft=300, save_ability="dexterity", dc=save_dc,
            damage_components=[
                SaveDamageComponent(dice_count=2, dice_size=8, damage_type="bludgeoning"),
                SaveDamageComponent(dice_count=4, dice_size=6, damage_type="cold"),
            ],
            success_damage="half", animation="ice-storm",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Ice Storm.")
        raise


def thunderwave_2014(save_dc: int) -> SpellSaveAction:
    """Build 2014 Thunderwave: 2d8 thunder, Constitution half."""
    try:
        return SpellSaveAction(
            id="thunderwave", name="Thunderwave", level=1, action_cost="action",
            range_ft=0, save_ability="constitution", dc=save_dc,
            damage_dice_count=2, damage_dice_size=8, damage_type="thunder",
            success_damage="half", upcast_dice_per_level=1, animation="thunderwave",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Thunderwave.")
        raise


def sacred_flame_2014(save_dc: int) -> SpellSaveAction:
    """Build 2014 Sacred Flame: 1d8 radiant cantrip, Dexterity, no damage on success."""
    try:
        return SpellSaveAction(
            id="sacred-flame", name="Sacred Flame", level=0, action_cost="action",
            range_ft=60, save_ability="dexterity", dc=save_dc,
            damage_dice_count=1, damage_dice_size=8, damage_type="radiant",
            success_damage="none", animation="sacred-flame",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Sacred Flame.")
        raise

