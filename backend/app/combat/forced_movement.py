"""Iron Pit universal forced-displacement policy.

The source card retains printed movement riders, but the fixed arena ignores
all forced pushes/pulls. Callers still resolve damage, saves, and conditions.
"""
from __future__ import annotations

import logging
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _ignored_forced_movement(distance_ft: int, direction: str) -> int:
    """Return zero distance without touching positions or other effects."""
    try:
        if distance_ft < 0 or distance_ft % 5:
            raise ValueError("Forced movement distance must be a nonnegative multiple of 5 feet.")
        logger.debug("Iron Pit ignores %s forced displacement of %s feet.", direction, distance_ft)
        return 0
    except Exception:
        logger.exception("Invalid %s forced displacement request: %s feet.", direction, distance_ft)
        raise


def push_straight_away(
    mover: EncounterCombatant,
    source: EncounterCombatant,
    setup: EncounterSetup,
    distance_ft: int,
    *,
    round_number: int = 1,
) -> int:
    """Ignore forced push; keep the entire remaining source effect intact."""
    return _ignored_forced_movement(distance_ft, "push")


def pull_straight_toward(
    mover: EncounterCombatant,
    source: EncounterCombatant,
    setup: EncounterSetup,
    distance_ft: int,
    *,
    round_number: int = 1,
) -> int:
    """Ignore forced pull; keep the entire remaining source effect intact."""
    return _ignored_forced_movement(distance_ft, "pull")
