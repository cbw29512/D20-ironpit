from __future__ import annotations

import logging

from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.spells import DefensiveSpellAction

logger = logging.getLogger(__name__)
_SOURCE = "D&D Beyond Basic Rules 2024"


def death_ward_2024() -> DefensiveSpellAction:
    """2024 Death Ward on the universal zero-HP replacement + instant-kill block."""
    try:
        return DefensiveSpellAction(
            id="death-ward",
            name="Death Ward",
            level=4,
            action_cost="action",
            range_ft=5,
            duration_minutes=480,
            target_policy="friendly",
            target_count=1,
            concentration=False,
            priority=95,
            modifier_effects=[
                SpellModifierEffect(
                    kind="zero-hp-replacement",
                    replacement_hp=1,
                    prevents_instant_death=True,
                ),
            ],
            animation="death-ward",
            source=f"{_SOURCE}: Death Ward",
        )
    except Exception:
        logger.exception("Failed to build 2024 Death Ward.")
        raise
