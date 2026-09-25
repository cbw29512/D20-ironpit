from __future__ import annotations

import logging

from app.content.bard_2014_progression import bard_2014_level
from app.domain.d20_bonus_dice import D20BonusDieAction

logger = logging.getLogger(__name__)


def build_bardic_inspiration_2014(level: int) -> D20BonusDieAction:
    """Bind 2014 Bardic Inspiration to the universal d20 bonus-die grant schema."""
    try:
        row = bard_2014_level(level)
        return D20BonusDieAction(
            id="bardic-inspiration",
            name="Bardic Inspiration",
            action_cost="bonus_action",
            range_ft=60,
            target_mode="other_ally",
            resource_id="bardic-inspiration",
            resource_cost=1,
            dice_count=1,
            dice_size=row.bardic_inspiration_die,
            test_kinds=["attack", "saving_throw", "ability_check"],
            duration_rounds=100,
            exclusive_group="bardic-inspiration",
            priority=25,
            animation="inspiration",
        )
    except Exception:
        logger.exception("Failed to build 2014 Bardic Inspiration at level %s.", level)
        raise
