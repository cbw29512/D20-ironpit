"""Source-accurate 2014 Blur using the universal defensive spell modifier."""
from __future__ import annotations

import logging

from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.spells import DefensiveSpellAction

logger = logging.getLogger(__name__)


def blur_2014() -> DefensiveSpellAction:
    """One-minute Concentration; incoming attacks have Disadvantage except bypass senses."""
    try:
        return DefensiveSpellAction(
            id="blur",
            name="Blur",
            level=2,
            action_cost="action",
            range_ft=0,
            duration_minutes=1,
            target_policy="self",
            target_count=1,
            modifier_effects=[
                SpellModifierEffect(
                    kind="attacks-against-disadvantage",
                    bypass_attacker_senses=["blindsight", "truesight"],
                ),
            ],
            concentration=True,
            priority=70,
            animation="blur",
            source="D&D Basic Rules 2014: Blur",
        )
    except Exception:
        logger.exception("Failed to build universal 2014 Blur defensive spell.")
        raise
