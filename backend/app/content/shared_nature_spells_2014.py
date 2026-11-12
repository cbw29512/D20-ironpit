"""Shared 2014 nature spells; source cards own caster DC and spell membership.

No creature-specific runtime behavior. Effects reuse universal area saves,
timed conditions, terrain, and the existing Iron Pit movement restriction.
"""
from __future__ import annotations

import logging

from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def entangle_2014(save_dc: int) -> SpellSaveAction:
    """SRD 5.1 Entangle: Strength save, Restrained, escape, terrain, Concentration."""
    try:
        if type(save_dc) is not int or not 1 <= save_dc <= 40:
            raise ValueError("Entangle requires a printed Strength save DC.")
        return SpellSaveAction(
            id="entangle", name="Entangle", level=1, action_cost="action",
            range_ft=90,
            area=AreaTargeting(shape="cube", origin="point", length_ft=20),
            save_ability="strength", dc=save_dc,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="restrained", duration_rounds=10,
                expiry_timing="source_turn_end",
                escape_check_ability="strength", escape_check_dc=save_dc,
            ),
            concentration=True, duration_minutes=1,
            creates_difficult_terrain=True,
            difficult_terrain_duration_rounds=10, animation="entangle",
        )
    except Exception:
        logger.exception("Failed shared 2014 Entangle declaration.")
        raise


def thunderwave_2014(save_dc: int) -> SpellSaveAction:
    """SRD 5.1 Thunderwave: self-origin 15-ft cube, CON save, 2d8 Thunder."""
    try:
        if type(save_dc) is not int or not 1 <= save_dc <= 40:
            raise ValueError("Thunderwave requires a printed Constitution save DC.")
        return SpellSaveAction(
            id="thunderwave", name="Thunderwave", level=1,
            action_cost="action", range_ft=15,
            area=AreaTargeting(shape="cube", origin="self", length_ft=15),
            save_ability="constitution", dc=save_dc,
            damage_dice_count=2, damage_dice_size=8, damage_type="thunder",
            success_damage="half", upcast_dice_per_level=1,
            # Source push is retained in data; Iron Pit movement policy
            # determines whether its displacement can change grid position.
            failed_save_push_ft=10, animation="spell-save",
        )
    except Exception:
        logger.exception("Failed shared 2014 Thunderwave declaration.")
        raise
