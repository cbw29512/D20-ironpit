from __future__ import annotations

import logging
from typing import get_args

from app.domain.action_types import ConditionName
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)
_CONDITION_IDS = frozenset(get_args(ConditionName))
_CONTROL_KEYS = frozenset({
    "condition_id",
    "effect_id",
    "duration_rounds",
    "expiry_timing",
    "repeat_save_ability",
    "repeat_save_dc",
    "repeat_save_timing",
    "allowed_removal_action_ids",
    "source_effect_immunity_on_end",
    "ends_on_damage",
    "ends_if_source_incapacitated",
    "ends_if_source_dead",
    "speed_multiplier",
    "blocks_reactions",
    "action_bonus_exclusive",
    "max_attacks_per_turn",
    "d20_disadvantage_abilities",
    "disadvantage_strength_d20_tests",
    "armor_class_bonus",
    "saving_throw_flat_bonuses",
})


def _rider_id(control: dict[str, object]) -> str:
    condition_id = str(control.get("condition_id") or "").strip().casefold()
    if condition_id:
        return condition_id
    return str(control.get("effect_id") or "").strip().casefold()


def supports_failed_save_control_2014(action: object) -> bool:
    try:
        if not isinstance(action, dict):
            return False
        control = action.get("failure_control_effect")
        if control is None:
            return True
        if not isinstance(control, dict) or set(control) - _CONTROL_KEYS:
            return False
        rider_id = _rider_id(control)
        if not rider_id:
            return False
        if control.get("condition_id"):
            return rider_id in _CONDITION_IDS
        return True
    except Exception:
        logger.exception("Failed to classify a 2014 failed-save control rider.")
        raise


def compile_failed_save_control_2014(action: dict[str, object]) -> FailedSaveTimedEffect | None:
    try:
        if not supports_failed_save_control_2014(action):
            return None
        control = action.get("failure_control_effect")
        if not isinstance(control, dict):
            return None
        kwargs: dict[str, object] = {"effect_id": _rider_id(control)}
        if control.get("duration_rounds") is not None:
            kwargs["duration_rounds"] = int(control["duration_rounds"])
        if control.get("expiry_timing"):
            kwargs["expiry_timing"] = str(control["expiry_timing"])
        if control.get("repeat_save_ability"):
            kwargs["repeat_save_ability"] = str(control["repeat_save_ability"])
            kwargs["repeat_save_dc"] = int(control["repeat_save_dc"])
            kwargs["repeat_save_timing"] = str(control["repeat_save_timing"])
        if control.get("allowed_removal_action_ids"):
            kwargs["allowed_removal_action_ids"] = list(control["allowed_removal_action_ids"])
        if control.get("ends_on_damage"):
            kwargs["ends_on_damage"] = True
        if control.get("ends_if_source_incapacitated"):
            kwargs["ends_if_source_incapacitated"] = True
        if control.get("ends_if_source_dead"):
            kwargs["ends_if_source_dead"] = True
        if control.get("source_effect_immunity_on_end"):
            kwargs["source_effect_immunity_on_end"] = True
        if control.get("speed_multiplier") is not None:
            kwargs["speed_multiplier"] = float(control["speed_multiplier"])
        if control.get("blocks_reactions"):
            kwargs["blocks_reactions"] = True
        if control.get("action_bonus_exclusive"):
            kwargs["action_bonus_exclusive"] = True
        if control.get("max_attacks_per_turn") is not None:
            kwargs["max_attacks_per_turn"] = int(control["max_attacks_per_turn"])
        if control.get("d20_disadvantage_abilities"):
            kwargs["d20_disadvantage_abilities"] = list(control["d20_disadvantage_abilities"])
        if control.get("disadvantage_strength_d20_tests"):
            kwargs["disadvantage_strength_d20_tests"] = True
        if control.get("armor_class_bonus"):
            kwargs["armor_class_bonus"] = int(control["armor_class_bonus"])
        if control.get("saving_throw_flat_bonuses"):
            kwargs["saving_throw_flat_bonuses"] = list(control["saving_throw_flat_bonuses"])
        return FailedSaveTimedEffect(**kwargs)
    except Exception:
        logger.exception("Failed to compile a 2014 failed-save control rider.")
        raise
