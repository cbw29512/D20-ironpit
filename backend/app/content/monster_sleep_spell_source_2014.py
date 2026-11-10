"""Pinned 2014 Sleep source facts, independent of monster spell access.

No runtime action is certified here. The shared engine must separately bind
these data into generic casting, area, pool, condition, and resource mechanisms.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)
_PATH = Path(__file__).with_name("data") / "srd_5_1_sleep_spell_rules.json"


class SleepSpellRules2014(BaseModel):
    """Immutable external spell source, not mutable combatant state."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    schema_version: Literal[1]
    ruleset: Literal["2014"]
    spell_id: Literal["sleep"]
    spell_level: Literal[1]
    casting_action: Literal["action"]
    range_ft: int = Field(ge=5)
    area_shape: Literal["radius"]
    area_radius_ft: int = Field(ge=5)
    pool_dice_count: int = Field(ge=1)
    pool_dice_size: int = Field(ge=2)
    pool_extra_dice_per_upcast_level: int = Field(ge=1)
    duration_rounds: int = Field(ge=1)
    concentration: Literal[False]
    target_order: Literal["ascending_current_hp"]
    skip_unconscious: Literal[True]
    requires_full_current_hp_coverage: Literal[True]
    ends_on_damage: Literal[True]
    allowed_removal_action_ids: list[str]
    excluded_creature_types: list[str]
    excluded_condition_immunities: list[str]
    condition_id: Literal["unconscious"]
    source_url: str
    source_version: Literal["2014 Basic Rules"]


def sleep_spell_rules_2014() -> SleepSpellRules2014:
    """Reject unknown fields and wrong edition before any consumer uses source."""
    try:
        rules = SleepSpellRules2014.model_validate_json(_PATH.read_text(encoding="utf-8"))
        if (rules.range_ft, rules.area_radius_ft, rules.pool_dice_count,
                rules.pool_dice_size, rules.pool_extra_dice_per_upcast_level,
                rules.duration_rounds) != (90, 20, 5, 8, 2, 10):
            raise ValueError("2014 Sleep printed range, pool, or duration differs from pinned source.")
        if (rules.allowed_removal_action_ids != ["wake-sleeper"]
                or rules.excluded_creature_types != ["undead"]
                or rules.excluded_condition_immunities != ["charmed"]):
            raise ValueError("2014 Sleep source exclusions or waking rights changed.")
        return rules
    except Exception:
        logger.exception("2014 Sleep pinned spell source failed validation: %s", _PATH)
        raise
