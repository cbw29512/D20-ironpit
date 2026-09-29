from __future__ import annotations

import logging

from app.domain.spells import DefensiveSpellAction, SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def build_shatter_2024(save_dc: int) -> SpellSaveAction:
    """Build the explicit 2024 Shatter fingerprint."""
    try:
        return SpellSaveAction(
            id="shatter",
            name="Shatter",
            level=2,
            action_cost="action",
            range_ft=60,
            area=AreaTargeting(shape="radius", origin="point", radius_ft=10),
            save_ability="constitution",
            dc=save_dc,
            damage_dice_count=3,
            damage_dice_size=8,
            damage_type="thunder",
            success_damage="half",
            upcast_dice_per_level=1,
            animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2024 Shatter.")
        raise


def build_greater_invisibility_2024() -> DefensiveSpellAction:
    """Build the explicit 2024 Greater Invisibility fingerprint."""
    try:
        return DefensiveSpellAction(
            id="greater-invisibility",
            name="Greater Invisibility",
            level=4,
            action_cost="action",
            range_ft=5,
            duration_minutes=1,
            target_policy="friendly",
            target_count=1,
            condition_ids=["invisible"],
            concentration=True,
            priority=95,
            animation="greater-invisibility",
            source="D&D Beyond Basic Rules 2024: Greater Invisibility",
        )
    except Exception:
        logger.exception("Failed to build 2024 Greater Invisibility.")
        raise
