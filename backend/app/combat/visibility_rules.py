from __future__ import annotations

import logging

from app.combat.condition_rules import BLINDED, INVISIBLE, has_condition, invisibility_benefits_suppressed
from app.combat.effective_senses import (
    SENSE_BLINDSIGHT,
    SENSE_TRUESIGHT,
    effective_sense_range_ft,
    sense_is_suppressed,
    source_sense_range_ft,
)
from app.combat.grid_geometry import footprint_distance_ft
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)

__all__ = [
    "SENSE_BLINDSIGHT",
    "SENSE_TRUESIGHT",
    "can_see",
    "effective_sense_range_ft",
    "sense_is_suppressed",
    "source_sense_range_ft",
    "visibility_distance_ft",
]


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
