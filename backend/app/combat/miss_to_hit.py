from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)

_FEATURE_ID = "miss-to-hit-once-per-turn"


def resolve_miss_to_hit(attacker: CombatantState, hit: bool, turn_key: str | None) -> tuple[bool, bool]:
    """Convert one miss to a hit when a declarative feature grants that capability.

    The runtime key deliberately contains no class/feat name. A new source can reuse
    the same mechanic without adding a content-name branch to the attack resolver.
    """
    try:
        if hit or not attacker.template.progression_features.miss_to_hit_once_per_turn:
            return hit, False
        if not turn_key:
            logger.warning("miss_to_hit_skipped missing turn_key attacker=%s", attacker.template.id)
            return hit, False
        if attacker.feature_last_turn_keys.get(_FEATURE_ID) == turn_key:
            return hit, False
        attacker.feature_last_turn_keys[_FEATURE_ID] = turn_key
        logger.info("miss_to_hit_applied attacker=%s turn_key=%s", attacker.template.id, turn_key)
        return True, True
    except Exception:
        logger.exception("miss_to_hit_resolution_failed attacker=%s", attacker.template.id)
        raise
