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
                SaveDamageComponent(dice_count=4, dice_size=6, damage_type="fire"),
                SaveDamageComponent(dice_count=4, dice_size=6, damage_type="radiant"),
            ],
            animation="flame-strike",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Flame Strike.")
        raise
