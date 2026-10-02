from __future__ import annotations

import logging

from app.domain.models import DamageType, TimedSelfBuffAction

logger = logging.getLogger(__name__)


def build_monk_2024_timed_self_buffs(level: int) -> list[TimedSelfBuffAction]:
    """Bind 2024 Monk timed defenses to the shared timed self-buff engine."""
    try:
        if level < 18:
            return []
        return [
            TimedSelfBuffAction(
                id="superior-defense",
                name="Superior Defense",
                action_cost="action",
                activation_timing="start_turn",
                resource_id="focus-points",
                resource_cost=3,
                duration_rounds=10,
                damage_resistances=[item for item in DamageType if item != DamageType.FORCE],
                ends_if_source_incapacitated=True,
                ends_if_source_dead=True,
                expiry_timing="source_turn_start",
                priority=140,
                animation="superior-defense",
            )
        ]
    except Exception:
        logger.exception("Failed to build 2024 Monk timed self-buffs at level %s.", level)
        raise
