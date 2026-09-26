from __future__ import annotations

import logging

from app.content.bard_2014_progression import bard_2014_level
from app.domain.reaction_roll_penalties import ReactionRollPenaltyAction

logger = logging.getLogger(__name__)


def cutting_words_2014(level: int) -> ReactionRollPenaltyAction | None:
    """Bind 2014 Cutting Words to the universal reaction roll-penalty schema."""
    try:
        if not 1 <= level <= 20:
            raise ValueError("2014 Lore Bard level must be between 1 and 20.")
        if level < 3:
            return None
        row = bard_2014_level(level)
        return ReactionRollPenaltyAction(
            id="cutting-words",
            name="Cutting Words",
            range_ft=60,
            resource_id="bardic-inspiration",
            resource_cost=1,
            dice_count=1,
            dice_size=row.bardic_inspiration_die,
            roll_kinds=["attack", "ability_check", "damage"],
            requires_source_sight=True,
            requires_target_hearing=True,
            blocked_target_condition_immunity="charmed",
            priority=40,
            animation="cutting-words",
        )
    except Exception:
        logger.exception("Failed to build 2014 Cutting Words at level %s.", level)
        raise
