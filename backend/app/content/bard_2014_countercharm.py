from __future__ import annotations

import logging

from app.domain.timed_self_buffs import TimedFriendlySaveAura, TimedSelfBuffAction

logger = logging.getLogger(__name__)


def countercharm_2014() -> TimedSelfBuffAction:
    """2014 Countercharm expressed as an at-will live friendly save aura."""
    try:
        return TimedSelfBuffAction(
            id="countercharm",
            name="Countercharm",
            action_cost="action",
            duration_rounds=1,
            friendly_save_advantage_aura=TimedFriendlySaveAura(
                radius_ft=30,
                required_effect_tags=["charmed", "frightened"],
                requires_hearing=True,
            ),
            expiry_timing="source_turn_end",
            ends_if_source_incapacitated=True,
            ends_if_source_dead=True,
            priority=5,
            animation="countercharm",
        )
    except Exception:
        logger.exception("Failed to build 2014 Countercharm.")
        raise
