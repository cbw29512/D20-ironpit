from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

SENSE_BLINDSIGHT = "blindsight"
SENSE_TRUESIGHT = "truesight"
DEAFENED = "deafened"
BLINDSIGHT_REQUIRES_HEARING = "blindsight_requires_hearing"


def _sense_source(observer: Any) -> Any:
    """Return the immutable source object that owns printed sense ranges and flags."""
    try:
        nested = getattr(observer, "template", None)
        if nested is not None and (
            hasattr(nested, "blindsight_ft")
            or hasattr(nested, "truesight_ft")
            or hasattr(nested, BLINDSIGHT_REQUIRES_HEARING)
        ):
            return nested
        return observer
    except Exception:
        logger.exception("Failed to resolve sense source object.")
        raise


def _flag_enabled(observer: Any, flag_name: str) -> bool:
    try:
        if bool(getattr(observer, flag_name, False)):
            return True
        source = _sense_source(observer)
        return bool(getattr(source, flag_name, False)) if source is not None else False
    except Exception:
        logger.exception("Failed to read sense flag %s.", flag_name)
        raise


def _has_condition(observer: Any, condition_id: str) -> bool:
    try:
        effects = getattr(observer, "active_effect_ids", None) or ()
        if condition_id not in effects:
            return False
        template = getattr(observer, "template", None)
        if template is not None and hasattr(template, "condition_immunities"):
            from app.combat.condition_rules import has_condition

            return has_condition(observer, condition_id)
        return True
    except Exception:
        logger.exception(
            "Failed to read live condition %s for effective senses.",
            condition_id,
        )
        raise


def source_sense_range_ft(observer: Any, sense_id: str) -> int:
    """Return the immutable source-declared range for one special sense."""
    try:
        template = _sense_source(observer)
        if template is None:
            return 0
        if sense_id == SENSE_BLINDSIGHT:
            return max(0, int(getattr(template, "blindsight_ft", 0) or 0))
        if sense_id == SENSE_TRUESIGHT:
            return max(0, int(getattr(template, "truesight_ft", 0) or 0))
        return 0
    except Exception:
        logger.exception(
            "Failed to read source sense %s for %s.",
            sense_id,
            getattr(_sense_source(observer), "name", "?"),
        )
        raise


def sense_is_suppressed(observer: Any, sense_id: str) -> bool:
    """Return whether a live declarative suppressor currently disables this sense."""
    try:
        for item in getattr(observer, "active_modifiers", None) or []:
            if getattr(item, "suppressed_sense_id", None) == sense_id:
                return True
        if (
            sense_id == SENSE_BLINDSIGHT
            and _flag_enabled(observer, BLINDSIGHT_REQUIRES_HEARING)
            and _has_condition(observer, DEAFENED)
        ):
            return True
        grants = getattr(_sense_source(observer), "sense_suppressors", None) or ()
        for grant in grants:
            grant_sense = grant.get("sense_id") if isinstance(grant, dict) else getattr(grant, "sense_id", None)
            conditions = (
                grant.get("suppressed_while_conditions")
                if isinstance(grant, dict)
                else getattr(grant, "suppressed_while_conditions", ())
            ) or ()
            if grant_sense == sense_id and any(
                _has_condition(observer, condition_id) for condition_id in conditions
            ):
                return True
        return False
    except Exception:
        logger.exception(
            "Failed to resolve sense suppression for %s / %s.",
            getattr(_sense_source(observer), "name", "?"),
            sense_id,
        )
        raise


def effective_sense_range_ft(observer: Any, sense_id: str) -> int:
    """Return the live usable range of one special sense."""
    try:
        if sense_is_suppressed(observer, sense_id):
            return 0
        return source_sense_range_ft(observer, sense_id)
    except Exception:
        logger.exception(
            "Failed to resolve effective sense %s for %s.",
            sense_id,
            getattr(_sense_source(observer), "name", "?"),
        )
        raise
