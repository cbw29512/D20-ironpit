from __future__ import annotations

import logging

from app.domain.spells import DefensiveSpellAction

logger = logging.getLogger(__name__)


def greater_invisibility_2014() -> DefensiveSpellAction:
    """Build 2014 Greater Invisibility from the universal Invisible condition."""
    try:
        return DefensiveSpellAction(
            id="greater-invisibility",
            name="Greater Invisibility",
            level=4,
            action_cost="action",
            range_ft=5,
            duration_minutes=1,
            target_policy="friendly",
            target_count=1,
            condition_ids=["invisible"],
            concentration=True,
            priority=95,
            animation="greater-invisibility",
            source="D&D Basic Rules 2014: Greater Invisibility",
        )
    except Exception:
        logger.exception("Failed to build 2014 Greater Invisibility.")
        raise


def invisibility_2014() -> DefensiveSpellAction:
    """Build 2014 Invisibility from the universal Invisible condition."""
    try:
        return DefensiveSpellAction(
            id="invisibility",
            name="Invisibility",
            level=2,
            action_cost="action",
            range_ft=5,
            duration_minutes=60,
            target_policy="friendly",
            target_count=1,
            condition_ids=["invisible"],
            concentration=True,
            priority=90,
            animation="invisibility",
            source="D&D Basic Rules 2014: Invisibility",
        )
    except Exception:
        logger.exception("Failed to build 2014 Invisibility.")
        raise
