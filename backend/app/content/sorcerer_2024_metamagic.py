from __future__ import annotations

import logging

from app.domain.spell_cast_modifiers import (
    ResourceBackedSpellRangeModifier,
    ResourceBackedSpellSaveDisadvantage,
)

logger = logging.getLogger(__name__)


def heightened_spell_2024(*, waive_while_innate: bool = False) -> ResourceBackedSpellSaveDisadvantage:
    """2024 Heightened Spell: 2 Sorcery Points, one target has Disadvantage on the save."""
    try:
        return ResourceBackedSpellSaveDisadvantage(
            id="heightened-spell",
            name="Heightened Spell",
            resource_id="sorcery-points",
            resource_cost=2,
            target_policy="first-target",
            waived_while_source_effect_id="innate-sorcery" if waive_while_innate else None,
            waived_once_per_turn=waive_while_innate,
            priority=100,
            source="D&D Beyond Basic Rules 2024: Sorcerer, Metamagic",
        )
    except Exception:
        logger.exception("Failed to build 2024 Heightened Spell.")
        raise


def distant_spell_2024() -> ResourceBackedSpellRangeModifier:
    try:
        return ResourceBackedSpellRangeModifier(
            id="distant-spell",
            name="Distant Spell",
            resource_id="sorcery-points",
            resource_cost=1,
            range_multiplier=2,
            minimum_base_range_ft=5,
            priority=100,
            source="D&D Beyond Basic Rules 2024: Sorcerer, Metamagic",
        )
    except Exception:
        logger.exception("Failed to build 2024 Distant Spell.")
        raise
