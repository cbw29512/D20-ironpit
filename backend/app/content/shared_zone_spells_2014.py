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
