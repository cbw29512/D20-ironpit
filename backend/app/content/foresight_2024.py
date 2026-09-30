from __future__ import annotations

import logging

from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.spells import DefensiveSpellAction

logger = logging.getLogger(__name__)


def build_foresight_2024() -> DefensiveSpellAction:
    """Build the edition-specific 2024 Foresight defensive spell fingerprint."""
    try:
        return DefensiveSpellAction(
            id="foresight",
            name="Foresight",
            level=9,
            action_cost="action",
            range_ft=5,
            duration_minutes=480,
            target_policy="self",
            modifier_effects=[
                SpellModifierEffect(kind="d20-test-advantage"),
                SpellModifierEffect(kind="attacks-against-disadvantage"),
            ],
            concentration=False,
            free_opening_cast=True,
            priority=100,
            animation="foresight",
            source="D&D Beyond Basic Rules 2024: Foresight",
        )
    except Exception:
        logger.exception("Failed to build the 2024 Foresight spell fingerprint.")
        raise
