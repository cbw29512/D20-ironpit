"""Pinned 2014 Sleep spell parameters; source data only, not a combat resolver."""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
_PATH = Path(__file__).with_name("data") / "srd_5_1_sleep_spell_rules.json"
_REQUIRED = {
    "schema_version", "ruleset", "spell_id", "spell_level", "casting_action",
    "range_ft", "area_shape", "area_radius_ft", "pool_dice_count",
    "pool_dice_size", "pool_extra_dice_per_upcast_level", "duration_rounds",
    "concentration", "target_order", "skip_unconscious",
    "requires_full_current_hp_coverage", "ends_on_damage",
    "allowed_removal_action_ids", "excluded_creature_types",
    "excluded_condition_immunities", "condition_id", "source_url",
    "source_version",
}


def sleep_spell_rules_2014() -> dict[str, object]:
    """Load and fail closed on malformed or unexpectedly edited spell source data."""
    try:
        data = json.loads(_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or set(data) != _REQUIRED:
            raise ValueError("2014 Sleep spell source fields have changed.")
        if data["schema_version"] != 1 or data["ruleset"] != "2014" or data["spell_id"] != "sleep":
            raise ValueError("Expected pinned 2014 Sleep source.")
        if any(type(data[field]) is not int or data[field] <= 0 for field in (
            "spell_level", "range_ft", "area_radius_ft", "pool_dice_count",
            "pool_dice_size", "duration_rounds",
        )):
            raise ValueError("2014 Sleep numerical parameters are invalid.")
        if data["condition_id"] != "unconscious" or data["target_order"] != "ascending_current_hp":
            raise ValueError("2014 Sleep ordering or condition is unsupported.")
        return data
    except Exception:
        logger.exception("Failed to load pinned 2014 Sleep source parameters.")
        raise
