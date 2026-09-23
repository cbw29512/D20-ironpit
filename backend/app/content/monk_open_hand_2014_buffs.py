from __future__ import annotations

import logging

from app.domain.models import DamageType, TimedSelfBuffAction

logger = logging.getLogger(__name__)


def build_monk_2014_timed_self_buffs(level: int) -> list[TimedSelfBuffAction]:
    try:
        if level < 18:
            return []
        return [TimedSelfBuffAction(
            id="empty-body",
            name="Empty Body",
            action_cost="action",
            resource_id="ki",
            resource_cost=4,
            duration_rounds=10,
            condition_ids=["invisible"],
            damage_resistances=[item for item in DamageType if item != DamageType.FORCE],
            expiry_timing="source_turn_start",
            priority=100,
            animation="empty-body",
        )]
    except Exception:
        logger.exception("Failed to build 2014 Monk timed self-buffs at level %s.", level)
        raise
