from __future__ import annotations

import logging

from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def build_sunburst(save_dc: int) -> SpellSaveAction:
    """Bind Sunburst to existing area-save and timed-condition primitives."""
    try:
        return SpellSaveAction(
            id="sunburst",
            name="Sunburst",
            level=8,
            action_cost="action",
            range_ft=150,
            area=AreaTargeting(
                shape="radius",
                origin="point",
                radius_ft=60,
            ),
            save_ability="constitution",
            dc=save_dc,
            damage_dice_count=12,
            damage_dice_size=6,
            damage_type="radiant",
            success_damage="half",
            effect_tags=["blinded"],
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="blinded",
                duration_rounds=10,
                expiry_timing="source_turn_start",
                repeat_save_ability="constitution",
                repeat_save_dc=save_dc,
                repeat_save_timing="target_turn_end",
            ),
            animation="sunburst",
        )
    except Exception:
        logger.exception("Failed to compile 2024 Cleric Sunburst.")
        raise
