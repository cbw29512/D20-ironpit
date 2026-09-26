from __future__ import annotations

import logging

from app.domain.spell_cast_modifiers import ResourceBackedSpellRangeModifier, ResourceBackedSpellSaveDisadvantage

logger = logging.getLogger(__name__)


def heightened_spell_2014() -> ResourceBackedSpellSaveDisadvantage:
    """Bind Heightened Spell to the universal resource-backed save Disadvantage primitive."""
    try:
        return ResourceBackedSpellSaveDisadvantage(
            id="heightened-spell",
            name="Heightened Spell",
            resource_id="sorcery-points",
            resource_cost=3,
            target_policy="first-target",
            priority=100,
            source="D&D Basic Rules 2014: Sorcerer 3, Metamagic",
        )
    except Exception:
        logger.exception("Failed to build 2014 Heightened Spell.")
        raise


def distant_spell_2014() -> ResourceBackedSpellRangeModifier:
    """Bind Distant Spell to the universal resource-backed spell-range primitive."""
    try:
        return ResourceBackedSpellRangeModifier(
            id="distant-spell",
            name="Distant Spell",
            resource_id="sorcery-points",
            resource_cost=1,
            range_multiplier=2,
            minimum_base_range_ft=5,
            priority=100,
            source="D&D Basic Rules 2014: Sorcerer 3, Metamagic",
        )
    except Exception:
        logger.exception("Failed to build 2014 Distant Spell.")
        raise
