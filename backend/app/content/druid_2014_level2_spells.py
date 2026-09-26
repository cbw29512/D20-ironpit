from __future__ import annotations

import logging

from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

logger = logging.getLogger(__name__)


def barkskin_2014() -> DefensiveSpellAction:
    try:
        return DefensiveSpellAction(
            id="barkskin",
            name="Barkskin",
            level=2,
            action_cost="action",
            range_ft=5,
            duration_minutes=60,
            target_policy="friendly",
            target_count=1,
            modifier_effects=[
                SpellModifierEffect(kind="armor-class-minimum", minimum_value=16),
            ],
            concentration=True,
            priority=10,
            animation="barkskin",
            source="D&D Basic Rules 2014: Barkskin",
        )
    except Exception:
        logger.exception("Failed to build 2014 Barkskin.")
        raise
