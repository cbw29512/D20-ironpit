"""Validation for source-declared persistent failed-save effects."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
_ABILITIES = frozenset({
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
})
_KEYS = frozenset({
    "save_ability", "dc", "effect_id", "curse_id",
    "cannot_regain_hit_points", "allowed_removal_action_ids",
    "delayed_max_hp_reduction_delay_hours",
    "delayed_max_hp_reduction_dice_count",
    "delayed_max_hp_reduction_dice_size",
    "delayed_max_hp_reduction_zero_kills",
})


def supported_save_persistent_2014(value: object) -> bool:
    try:
        if not isinstance(value, dict) or set(value) != _KEYS:
            return False
        removal = value["allowed_removal_action_ids"]
        return (
            str(value["save_ability"]).lower() in _ABILITIES
            and isinstance(value["dc"], int) and 0 < value["dc"] <= 40
            and isinstance(value["effect_id"], str) and bool(value["effect_id"].strip())
            and isinstance(value["curse_id"], str) and bool(value["curse_id"].strip())
            and isinstance(value["cannot_regain_hit_points"], bool)
            and isinstance(removal, list)
            and all(isinstance(item, str) and item.strip() for item in removal)
            and isinstance(value["delayed_max_hp_reduction_delay_hours"], int)
            and value["delayed_max_hp_reduction_delay_hours"] > 0
            and isinstance(value["delayed_max_hp_reduction_dice_count"], int)
            and 0 < value["delayed_max_hp_reduction_dice_count"] <= 40
            and isinstance(value["delayed_max_hp_reduction_dice_size"], int)
            and 2 <= value["delayed_max_hp_reduction_dice_size"] <= 100
            and isinstance(value["delayed_max_hp_reduction_zero_kills"], bool)
        )
    except Exception:
        logger.exception("Failed to validate 2014 persistent save-effect data.")
        raise
