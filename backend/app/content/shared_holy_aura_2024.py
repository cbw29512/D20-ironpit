from __future__ import annotations

import logging

from app.domain.timed_self_buffs import TimedFriendlySaveAura, TimedSelfBuffAction

logger = logging.getLogger(__name__)


def holy_aura_2024(save_dc: int) -> TimedSelfBuffAction:
    """2024 Holy Aura: 30-ft ally save Advantage and attacks-against Disadvantage."""
    try:
        if not 1 <= save_dc <= 40:
            raise ValueError("Holy Aura requires a certified spell save DC.")
        return TimedSelfBuffAction(
            id="holy-aura",
            name="Holy Aura",
            action_cost="action",
            resource_id="spell-slot-8",
            resource_cost=1,
            duration_rounds=10,
            concentration=True,
            priority=50,
            animation="holy-aura",
            friendly_save_advantage_aura=TimedFriendlySaveAura(
                radius_ft=30,
                all_saves=True,
                attacks_against_disadvantage=True,
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Holy Aura.")
        raise
