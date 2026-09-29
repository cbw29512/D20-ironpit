from __future__ import annotations

import logging

from app.content.bard_combat_levels import BARD_COMBAT_LEVELS
from app.domain.reaction_roll_penalties import ReactionRollPenaltyAction

logger = logging.getLogger(__name__)


def build_cutting_words_2024(level: int) -> ReactionRollPenaltyAction:
    """Bind 2024 Cutting Words to the universal reaction roll-penalty schema."""
    try:
        row = BARD_COMBAT_LEVELS.get(level)
        if row is None or level < 3:
            raise ValueError("2024 Cutting Words requires Bard level 3 or higher.")
        return ReactionRollPenaltyAction(
            id="cutting-words",
            name="Cutting Words",
            range_ft=60,
            resource_id="bardic-inspiration",
            resource_cost=1,
            dice_count=1,
            dice_size=row.bardic_die_size,
            roll_kinds=["attack", "ability_check", "damage"],
            requires_source_sight=True,
            requires_target_hearing=False,
            blocked_target_condition_immunity=None,
            priority=40,
            animation="cutting-words",
        )
    except Exception:
        logger.exception("Failed to build 2024 Cutting Words at level %s.", level)
        raise
