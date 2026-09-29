from __future__ import annotations

import logging

from app.content.bard_combat_levels import BARD_COMBAT_LEVELS
from app.domain.d20_bonus_dice import D20BonusDieAction

logger = logging.getLogger(__name__)


def build_bardic_inspiration_2024(level: int) -> D20BonusDieAction:
    """Bind 2024 Bardic Inspiration to the universal failed-D20-test bonus-die grant."""
    try:
        row = BARD_COMBAT_LEVELS.get(level)
        if row is None:
            raise ValueError("2024 Bardic Inspiration supports Bard levels 1 through 20.")
        return D20BonusDieAction(
            id="bardic-inspiration",
            name="Bardic Inspiration",
            action_cost="bonus_action",
            range_ft=60,
            target_mode="other_ally",
            resource_id="bardic-inspiration",
            resource_cost=1,
            dice_count=1,
            dice_size=row.bardic_die_size,
            test_kinds=["attack", "saving_throw", "ability_check"],
            duration_rounds=600,
            exclusive_group="bardic-inspiration",
            priority=25,
            animation="inspiration",
        )
    except Exception:
        logger.exception("Failed to build 2024 Bardic Inspiration at level %s.", level)
        raise
