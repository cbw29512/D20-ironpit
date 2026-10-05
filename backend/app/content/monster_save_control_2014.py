from __future__ import annotations

import logging
from typing import get_args

from app.domain.action_types import ConditionName
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)
_CONDITION_IDS = frozenset(get_args(ConditionName))
_CONTROL_KEYS = frozenset({
    "condition_id",
    "duration_rounds",
    "expiry_timing",
    "repeat_save_ability",
    "repeat_save_dc",
    "repeat_save_timing",
    "source_effect_immunity_on_end",
    "ends_on_damage",
    "ends_if_source_incapacitated",
    "ends_if_source_dead",
})


def supports_failed_save_control_2014(action: object) -> bool:
    try:
        if not isinstance(action, dict):
            return False
        control = action.get("failure_control_effect")
        if control is None:
            return True
        if not isinstance(control, dict) or set(control) - _CONTROL_KEYS:
            return False
        condition_id = str(control.get("condition_id") or "").strip().casefold()
        return condition_id in _CONDITION_IDS
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
        kwargs: dict[str, object] = {
            "effect_id": str(control["condition_id"]).strip().casefold(),
        }
        if control.get("duration_rounds") is not None:
            kwargs["duration_rounds"] = int(control["duration_rounds"])
        if control.get("expiry_timing"):
            kwargs["expiry_timing"] = str(control["expiry_timing"])
        if control.get("repeat_save_ability"):
            kwargs["repeat_save_ability"] = str(control["repeat_save_ability"])
            kwargs["repeat_save_dc"] = int(control["repeat_save_dc"])
            kwargs["repeat_save_timing"] = str(control["repeat_save_timing"])
        if control.get("ends_on_damage"):
            kwargs["ends_on_damage"] = True
        if control.get("ends_if_source_incapacitated"):
            kwargs["ends_if_source_incapacitated"] = True
        if control.get("ends_if_source_dead"):
            kwargs["ends_if_source_dead"] = True
        # source_effect_immunity_on_end stays in _CONTROL_KEYS so printed
        # 24h/cross-fight flags do not fail-closed, but they are never compiled.
        return FailedSaveTimedEffect(**kwargs)
    except Exception:
        logger.exception("Failed to compile a 2014 failed-save control rider.")
        raise
