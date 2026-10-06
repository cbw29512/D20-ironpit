from __future__ import annotations

from typing import get_args

from app.content.monster_zero_hp_save_rider_2014 import (
    ZERO_HP_SAVE_RIDER_KEYS_2014,
    supports_zero_hp_save_rider_2014,
)
from app.domain.action_types import ConditionName, ConditionTiming
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType

_DAMAGE_TYPES = frozenset(item.value for item in DamageType)
_DAMAGE_KEYS = frozenset({"average", "bonus", "dice_count", "dice_size", "type"})
_CONTROL_KEYS = frozenset({"grapple_escape_dc", "max_target_size", "restrains_while_grappled"})
_SAVE_CONDITION_KEYS = frozenset({
    "condition_id", "dc", "max_target_size", "save_ability",
    "duration_rounds", "repeat_save_timing", "repeat_save_failure_condition_id",
    "failure_push_ft", "excluded_creature_types", "excluded_creature_subtypes",
})
_SAVE_DAMAGE_KEYS = frozenset({
    "damage_bonus", "damage_dice_count", "damage_dice_size", "damage_type",
    "dc", "save_ability", "success_damage",
}) | ZERO_HP_SAVE_RIDER_KEYS_2014
_ABILITIES = frozenset({
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
})
_CONDITIONS = frozenset(get_args(ConditionName))
_TIMINGS = frozenset(get_args(ConditionTiming))
ADVANTAGE_TRIGGERS_2014 = frozenset({"target_grappled_by_self"})


def optional_size_2014(value: object) -> bool:
    return value is None or str(value).lower() in {item.value for item in CreatureSize}


def optional_name_list_2014(value: object) -> bool:
    return value is None or (
        isinstance(value, list)
        and all(isinstance(item, str) and str(item).strip() for item in value)
    )


def supported_damage_row_2014(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _DAMAGE_KEYS:
        return False
    damage_type = str(value.get("type", "")).lower()
    return (
        isinstance(value.get("dice_count"), int) and int(value["dice_count"]) > 0
        and isinstance(value.get("dice_size"), int) and int(value["dice_size"]) >= 2
        and isinstance(value.get("bonus", 0), int)
        and damage_type in _DAMAGE_TYPES
    )


def supported_control_2014(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _CONTROL_KEYS:
        return False
    return (
        isinstance(value.get("grapple_escape_dc"), int)
        and int(value["grapple_escape_dc"]) > 0
        and isinstance(value.get("restrains_while_grappled", False), bool)
        and optional_size_2014(value.get("max_target_size"))
    )


def supported_save_condition_2014(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _SAVE_CONDITION_KEYS:
        return False
    duration = value.get("duration_rounds")
    timing = value.get("repeat_save_timing")
    escalation = value.get("repeat_save_failure_condition_id")
    if timing is not None and duration is None and escalation is None:
        return False
    if escalation is not None and (
        timing is None or str(escalation).lower() not in _CONDITIONS
    ):
        return False
    push = value.get("failure_push_ft", 0)
    if not isinstance(push, int) or push < 0 or push % 5:
        return False
    return (
        str(value.get("condition_id", "")).lower() in _CONDITIONS
        and isinstance(value.get("dc"), int) and 0 < int(value["dc"]) <= 40
        and str(value.get("save_ability", "")).lower() in _ABILITIES
        and optional_size_2014(value.get("max_target_size"))
        and (duration is None or isinstance(duration, int) and 0 < duration <= 100800)
        and (timing is None or str(timing).lower() in _TIMINGS)
        and optional_name_list_2014(value.get("excluded_creature_types"))
        and optional_name_list_2014(value.get("excluded_creature_subtypes"))
    )


def supported_save_damage_2014(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _SAVE_DAMAGE_KEYS:
        return False
    required = {
        "damage_dice_count", "damage_dice_size", "damage_type",
        "dc", "save_ability", "success_damage",
    }
    return (
        required <= set(value)
        and isinstance(value["damage_dice_count"], int) and value["damage_dice_count"] > 0
        and isinstance(value["damage_dice_size"], int) and value["damage_dice_size"] >= 2
        and isinstance(value.get("damage_bonus", 0), int)
        and str(value["damage_type"]).lower() in _DAMAGE_TYPES
        and isinstance(value["dc"], int) and 0 < value["dc"] <= 40
        and str(value["save_ability"]).lower() in _ABILITIES
        and value["success_damage"] in {"none", "half"}
        and supports_zero_hp_save_rider_2014(value)
    )


def supported_save_max_hp_reduction_2014(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    allowed = {
        "save_ability", "dc", "max_hp_reduction_equals_damage_taken", "zero_max_hp_kills",
    }
    return (
        set(value) <= allowed
        and value.get("max_hp_reduction_equals_damage_taken") is True
        and str(value.get("save_ability", "")).lower() in _ABILITIES
        and isinstance(value.get("dc"), int) and 0 < int(value["dc"]) <= 40
        and isinstance(value.get("zero_max_hp_kills", False), bool)
    )


def supported_contested_movement_2014(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if set(value) != {
        "source_ability", "target_ability", "max_target_size", "distance_ft", "direction",
    }:
        return False
    return (
        str(value["source_ability"]).lower() in _ABILITIES
        and str(value["target_ability"]).lower() in _ABILITIES
        and optional_size_2014(value.get("max_target_size"))
        and isinstance(value["distance_ft"], int)
        and value["distance_ft"] >= 0
        and value["distance_ft"] % 5 == 0
        and value["direction"] in {"toward_source", "away_from_source"}
    )
