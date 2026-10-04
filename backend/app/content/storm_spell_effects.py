from __future__ import annotations

import logging

from app.domain.save_damage import SaveDamageComponent
from app.domain.spells import SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def build_fire_storm_2024(save_dc: int) -> SpellSaveAction:
    """2024 Fire Storm: ten face-adjacent 10-foot cubes, Dexterity 7d10 Fire, half."""
    try:
        return SpellSaveAction(
            id="fire-storm",
            name="Fire Storm",
            level=7,
            action_cost="action",
            range_ft=150,
            area=AreaTargeting(
                shape="cube",
                origin="point",
                length_ft=10,
                contiguous_section_count=10,
            ),
            save_ability="dexterity",
            dc=save_dc,
            damage_dice_count=7,
            damage_dice_size=10,
            damage_type="fire",
            success_damage="half",
            animation="fire-storm",
            source="D&D Beyond Basic Rules 2024: Fire Storm",
        )
    except Exception:
        logger.exception("Failed to build 2024 Fire Storm.")
        raise


def build_ice_storm_2024(save_dc: int) -> SpellSaveAction:
    """2024 Ice Storm: 20-foot cylinder, mixed Bludgeoning/Cold, temporary Difficult Terrain."""
    try:
        return SpellSaveAction(
            id="ice-storm",
            name="Ice Storm",
            level=4,
            action_cost="action",
            range_ft=300,
            area=AreaTargeting(shape="radius", origin="point", radius_ft=20),
            save_ability="dexterity",
            dc=save_dc,
            success_damage="half",
            damage_components=[
                SaveDamageComponent(dice_count=2, dice_size=10, damage_type="bludgeoning"),
                SaveDamageComponent(dice_count=4, dice_size=8, damage_type="cold"),
            ],
            upcast_dice_per_level=0,
            creates_difficult_terrain=True,
            difficult_terrain_duration_rounds=1,
            animation="ice-storm",
            source="D&D Beyond Basic Rules 2024: Ice Storm",
        )
    except Exception:
        logger.exception("Failed to build 2024 Ice Storm.")
        raise
