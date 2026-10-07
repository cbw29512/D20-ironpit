from __future__ import annotations

import logging

from app.domain.actions import ConditionTiming
from app.domain.timed_effects import TimedEffect

logger = logging.getLogger(__name__)


def timed_effect_expiry_due(
    effect: TimedEffect,
    round_number: int,
    timing: ConditionTiming,
    target_turns_started: int | None = None,
) -> bool:
    """Return whether a timed effect's declared expiry boundary has been reached."""
    try:
        if effect.expiry_timing != timing:
            return False
        if effect.expires_round is not None and round_number < effect.expires_round:
            return False
        if effect.expires_target_turn_count is not None:
            return (
                target_turns_started is not None
                and target_turns_started >= effect.expires_target_turn_count
            )
        return True
    except Exception:
        logger.exception("Failed timed effect expiry check for %s.", effect.effect_id)
        raise
