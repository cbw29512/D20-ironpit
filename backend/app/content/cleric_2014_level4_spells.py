from __future__ import annotations

import logging

from app.domain.spells import DefensiveSpellAction
from app.domain.zero_hp_effects import SurvivalWard

logger = logging.getLogger(__name__)


def death_ward_2014() -> DefensiveSpellAction:
    """Compile 2014 Death Ward onto the generic one-shot survival-ward primitive."""
    try:
        return DefensiveSpellAction(
            id="death-ward",
            name="Death Ward",
            level=4,
            action_cost="action",
            range_ft=5,
            duration_minutes=480,
            target_policy="friendly",
            survival_ward=SurvivalWard(
                replacement_hp=1,
                prevents_nondamage_instant_death=True,
            ),
            priority=40,
            animation="death-ward",
            source="D&D Basic Rules 2014: Death Ward",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Death Ward.")
        raise
