from __future__ import annotations

import logging

from app.domain.progression import ProgressionCombatFeatures
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)

_FEATURE_KEY = "miss_to_hit_once_per_turn"


def resolve_miss_to_hit(
    *,
    features: ProgressionCombatFeatures,
    state: CombatantState,
    turn_key: str | None,
    attack_hit: bool,
) -> bool:
    """Convert the first eligible miss in a turn to a hit when declared by data."""
    try:
        if attack_hit or not features.miss_to_hit_once_per_turn:
            return attack_hit
        if not turn_key:
            logger.warning("miss-to-hit resolution skipped: missing turn identity")
            return False
        if state.feature_last_turn_keys.get(_FEATURE_KEY) == turn_key:
            return False
        state.feature_last_turn_keys[_FEATURE_KEY] = turn_key
        logger.info("miss-to-hit applied for turn %s", turn_key)
        return True
    except Exception:
        logger.exception("miss-to-hit resolution failed")
        return attack_hit
