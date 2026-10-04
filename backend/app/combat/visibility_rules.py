from __future__ import annotations

import logging

from app.combat.condition_rules import BLINDED, INVISIBLE, has_condition, invisibility_benefits_suppressed
from app.combat.grid_geometry import footprint_distance_ft
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)

SENSE_BLINDSIGHT = "blindsight"
SENSE_TRUESIGHT = "truesight"


def source_sense_range_ft(observer: CombatantState, sense_id: str) -> int:
    """Return the immutable source-declared range for one special sense."""
    try:
        template = getattr(observer, "template", None)
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
            getattr(getattr(observer, "template", None), "name", "?"),
        )
        raise


def sense_is_suppressed(observer: CombatantState, sense_id: str) -> bool:
    """Return whether a live declarative suppressor currently disables this sense.

    Issue #535 binds suppressor data here. This tranche only exposes the hook.
    """
    try:
        for item in getattr(observer, "active_modifiers", None) or []:
            if getattr(item, "suppressed_sense_id", None) == sense_id:
                return True
        grants = getattr(getattr(observer, "template", None), "sense_suppressors", None) or ()
        for grant in grants:
            grant_sense = grant.get("sense_id") if isinstance(grant, dict) else getattr(grant, "sense_id", None)
            conditions = (
                grant.get("suppressed_while_conditions")
                if isinstance(grant, dict)
                else getattr(grant, "suppressed_while_conditions", ())
            ) or ()
            if grant_sense == sense_id and any(
                has_condition(observer, condition_id) for condition_id in conditions
            ):
                return True
        return False
    except Exception:
        logger.exception(
            "Failed to resolve sense suppression for %s / %s.",
            getattr(getattr(observer, "template", None), "name", "?"),
            sense_id,
        )
        raise


def effective_sense_range_ft(observer: CombatantState, sense_id: str) -> int:
    """Return the live usable range of one special sense."""
    try:
        if sense_is_suppressed(observer, sense_id):
            return 0
        return source_sense_range_ft(observer, sense_id)
    except Exception:
        logger.exception(
            "Failed to resolve effective sense %s for %s.",
            sense_id,
            getattr(getattr(observer, "template", None), "name", "?"),
        )
        raise


def visibility_distance_ft(
    observer: CombatantState,
    target: CombatantState,
    distance_ft: int | None = None,
) -> int | None:
    """Use the caller-supplied distance, or authoritative stored grid positions."""
    try:
        if distance_ft is not None:
            return int(distance_ft)
        observer_position = getattr(observer, "position", None)
        target_position = getattr(target, "position", None)
        observer_template = getattr(observer, "template", None)
        target_template = getattr(target, "template", None)
        if observer_position is None or target_position is None:
            return None
        if observer_template is None or target_template is None:
            return None
        return footprint_distance_ft(
            observer_position,
            observer_template.size,
            target_position,
            target_template.size,
        )
    except Exception:
        logger.exception("Failed to resolve visibility distance.")
        raise


def _sense_reaches(observer: CombatantState, sense_id: str, distance_ft: int | None) -> bool:
    if distance_ft is None:
        return False
    return effective_sense_range_ft(observer, sense_id) >= distance_ft


def can_see(
    observer: CombatantState,
    target: CombatantState,
    distance_ft: int | None = None,
) -> bool:
    """Return whether the observer can perceive the target under supported visibility rules."""
    try:
        resolved_distance = visibility_distance_ft(observer, target, distance_ft)
        target_hidden = has_condition(target, INVISIBLE) and not invisibility_benefits_suppressed(target)
        blinded = has_condition(observer, BLINDED)
        # Blindsight perceives without sight, including Invisible targets, inside its range.
        if _sense_reaches(observer, SENSE_BLINDSIGHT, resolved_distance):
            return True
        # Truesight is visual: Blinded blocks it. Inside range it sees Invisible.
        if blinded:
            return False
        if target_hidden:
            return _sense_reaches(observer, SENSE_TRUESIGHT, resolved_distance)
        return True
    except Exception:
        logger.exception(
            "Failed to resolve visibility between %s and %s.",
            getattr(getattr(observer, "template", None), "name", "?"),
            getattr(getattr(target, "template", None), "name", "?"),
        )
        raise
