from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)
_FEATURE_KEY = "miss-to-hit-once-per-turn"


def resolve_miss_to_hit(
    state: CombatantState,
    attack_hit: bool,
    turn_key: str | None,
) -> tuple[bool, bool]:
    """Convert the first eligible miss in a turn to a hit when declared by progression data."""
    try:
        if attack_hit or not state.template.progression_features.miss_to_hit_once_per_turn:
            return bool(attack_hit), False
        if not turn_key:
            logger.warning("miss-to-hit resolution skipped: missing turn identity")
            return False, False
        if state.feature_last_turn_keys.get(_FEATURE_KEY) == turn_key:
            return False, False
        state.feature_last_turn_keys[_FEATURE_KEY] = turn_key
        logger.info("miss-to-hit applied for turn %s", turn_key)
        return True, True
    except Exception:
        logger.exception("miss-to-hit resolution failed")
        return bool(attack_hit), False
