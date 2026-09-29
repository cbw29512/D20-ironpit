from __future__ import annotations

import logging

from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def build_disintegrate_2024(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="disintegrate", name="Disintegrate", level=6, action_cost="action",
            range_ft=60, save_ability="dexterity", dc=save_dc,
            damage_dice_count=10, damage_dice_size=6, damage_bonus=40,
            damage_type="force", success_damage="none", upcast_dice_per_level=3,
            animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2024 Disintegrate.")
        raise


def build_finger_of_death_2024(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="finger-of-death", name="Finger of Death", level=7, action_cost="action",
            range_ft=60, save_ability="constitution", dc=save_dc,
            damage_dice_count=7, damage_dice_size=8, damage_bonus=30,
            damage_type="necrotic", success_damage="half", animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2024 Finger of Death.")
        raise


def build_sunburst_2024(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="sunburst", name="Sunburst", level=8, action_cost="action",
            range_ft=150,
            area=AreaTargeting(shape="radius", origin="point", radius_ft=60),
            save_ability="constitution", dc=save_dc,
            damage_dice_count=12, damage_dice_size=6, damage_type="radiant",
            success_damage="half",
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="blinded", duration_rounds=10, expiry_timing="target_turn_end",
                repeat_save_ability="constitution", repeat_save_dc=save_dc,
                repeat_save_timing="target_turn_end",
            ),
            animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2024 Sunburst.")
        raise


def build_cone_of_cold_2024(save_dc: int) -> SpellSaveAction:
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
        logger.exception("Failed to build 2024 Cone of Cold.")
        raise
