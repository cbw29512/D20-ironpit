from __future__ import annotations

import logging

from app.domain.persistent_save_zones import PersistentSaveZoneAction

logger = logging.getLogger(__name__)
_SOURCE = "D&D Basic Rules 2014 / SRD 5.1"


def wall_of_fire_2014(save_dc: int) -> PersistentSaveZoneAction:
    """Build the deterministic 2014 ring-wall option on the shared zone engine."""
    try:
        return PersistentSaveZoneAction(
            id="wall-of-fire",
            name="Wall of Fire",
            level=4,
            action_cost="action",
            cast_range_ft=120,
            radius_ft=10,
            duration_rounds=10,
            concentration=True,
            save_ability="dexterity",
            dc=save_dc,
            triggers=["appear", "enter", "end_turn"],
            save_triggers=["appear"],
            once_per_turn=True,
            target_policy="enemies",
            save_context="spell",
            damage_dice_count=5,
            damage_dice_size=8,
            damage_type="fire",
            success_damage="half",
            upcast_dice_per_level=1,
            animation="wall-of-fire",
            source=f"{_SOURCE}: Wall of Fire",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Wall of Fire.")
        raise


def insect_plague_2014(save_dc: int) -> PersistentSaveZoneAction:
    """2014 SRD Insect Plague via universal recurring save, terrain and area state.

    The cast creates a lightly obscured, Difficult Terrain radius; current Pit
    combat has no source-independent sight-based Perception Action. The generic
    zone retains that environment tag without inventing attack disadvantage.
    """
    try:
        return PersistentSaveZoneAction(
            id="insect-plague",
            name="Insect Plague",
            level=5,
            action_cost="action",
            cast_range_ft=300,
            radius_ft=20,
            duration_rounds=100,
            concentration=True,
            creates_difficult_terrain=True,
            lightly_obscured=True,
            save_ability="constitution",
            dc=save_dc,
            triggers=["appear", "enter", "end_turn"],
            once_per_turn=True,
            target_policy="all",
            save_context="spell",
            damage_dice_count=4,
            damage_dice_size=10,
            damage_type="piercing",
            success_damage="half",
            upcast_dice_per_level=1,
            animation="insect-plague",
            source=f"{_SOURCE}: Insect Plague",
        )
    except Exception:
        logger.exception("Failed to build source-neutral 2014 Insect Plague.")
        raise
