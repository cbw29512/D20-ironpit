from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def timed_speed_multiplier(state: CombatantState) -> float:
    """Product of active timed-effect speed multipliers; 1.0 when none apply."""
    try:
        multiplier = 1.0
        for effect in state.timed_effects:
            limits = effect.control_limits
            if limits is None:
                continue
            multiplier *= limits.speed_multiplier
        return multiplier
    except Exception:
        logger.exception("Failed to resolve timed-effect speed multiplier for %s.", state.template.name)
        raise
