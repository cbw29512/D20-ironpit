from __future__ import annotations

import logging
from typing import get_args

from app.domain.action_types import ConditionName, ConditionTiming
from app.domain.failure_margin import FailureMarginEscalation, require_escalation_duration
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_DAMAGE_TYPES = frozenset(item.value for item in DamageType)
_ABILITIES = frozenset({
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
})
_CONDITIONS = frozenset(get_args(ConditionName))
_TIMINGS = frozenset(get_args(ConditionTiming))
_KEYS = frozenset({
    "condition_id", "dc", "max_target_size", "save_ability",
    "duration_rounds", "repeat_save_timing", "repeat_save_failure_condition_id",
    "failure_push_ft", "excluded_creature_types", "excluded_creature_subtypes",
    "cannot_regain_hit_points", "failure_margin_escalation",
    "start_of_turn_damage_dice_count", "start_of_turn_damage_dice_size",
    "start_of_turn_damage_type",
})


def _optional_size(value: object) -> bool:
    try:
        return value is None or str(value).lower() in {item.value for item in CreatureSize}
    except Exception:
        logger.exception("Failed to validate optional creature size.")
        raise


def _optional_names(value: object) -> bool:
    try:
        return value is None or (
            isinstance(value, list)
            and all(isinstance(item, str) and str(item).strip() for item in value)
        )
    except Exception:
        logger.exception("Failed to validate optional source-name list.")
        raise


def supported_save_condition_2014(value: object) -> bool:
    """Validate source-neutral failed-save condition data, including indefinite repeat saves."""
    try:
        if not isinstance(value, dict) or not set(value) <= _KEYS:
            return False
        duration = value.get("duration_rounds")
        timing = value.get("repeat_save_timing")
        escalation = value.get("repeat_save_failure_condition_id")
        if escalation is not None and (
            timing is None or str(escalation).lower() not in _CONDITIONS
        ):
            return False
        margin = value.get("failure_margin_escalation")
        if margin is not None:
            try:
                rule = FailureMarginEscalation.model_validate(margin)
                require_escalation_duration(rule, duration)
            except (ValueError, TypeError):
                return False
        push = value.get("failure_push_ft", 0)
        if not isinstance(push, int) or push < 0 or push % 5:
            return False
        start_count = value.get("start_of_turn_damage_dice_count", 0)
        start_size = value.get("start_of_turn_damage_dice_size", 6)
        start_type = value.get("start_of_turn_damage_type")
        if not isinstance(start_count, int) or not 0 <= start_count <= 40:
            return False
        if not isinstance(start_size, int) or not 2 <= start_size <= 100:
            return False
        valid_start_type = (
            str(start_type).lower() in _DAMAGE_TYPES if start_type is not None else False
        )
        if (start_count > 0) != valid_start_type:
            return False
        return (
            str(value.get("condition_id", "")).lower() in _CONDITIONS
            and isinstance(value.get("dc"), int) and 0 < int(value["dc"]) <= 40
            and str(value.get("save_ability", "")).lower() in _ABILITIES
            and _optional_size(value.get("max_target_size"))
            and isinstance(value.get("cannot_regain_hit_points", False), bool)
            and (duration is None or isinstance(duration, int) and 0 < duration <= 100800)
            and (timing is None or str(timing).lower() in _TIMINGS)
            and _optional_names(value.get("excluded_creature_types"))
            and _optional_names(value.get("excluded_creature_subtypes"))
        )
    except Exception:
        logger.exception("Failed to validate 2014 save-condition source data.")
        raise
