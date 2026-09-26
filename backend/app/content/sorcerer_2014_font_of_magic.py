from __future__ import annotations

import logging

from app.content.sorcerer_2014_progression import sorcerer_2014_level
from app.domain.resource_conversion import ResourceConversionAction

logger = logging.getLogger(__name__)

_SLOT_CREATION_COST = {1: 2, 2: 3, 3: 5, 4: 6, 5: 7}


def font_of_magic_2014_actions(level: int) -> list[ResourceConversionAction]:
    """Build every legal Flexible Casting exchange unlocked at this Sorcerer level."""
    try:
        if not 2 <= level <= 20:
            raise ValueError("2014 Font of Magic requires Sorcerer level 2 or higher.")
        row = sorcerer_2014_level(level)
        highest_slot = max(
            (spell_level for spell_level, uses in enumerate(row.spell_slots, start=1) if uses),
            default=0,
        )
        highest_convertible = min(5, highest_slot)
        actions: list[ResourceConversionAction] = []
        for spell_level in range(1, highest_convertible + 1):
            actions.append(ResourceConversionAction(
                id=f"create-spell-slot-{spell_level}",
                name=f"Font of Magic: Create {spell_level}{'st' if spell_level == 1 else 'nd' if spell_level == 2 else 'rd' if spell_level == 3 else 'th'}-Level Spell Slot",
                action_cost="bonus_action",
                source_resource_id="sorcery-points",
                source_cost=_SLOT_CREATION_COST[spell_level],
                target_resource_id=f"spell-slot-{spell_level}",
                target_gain=1,
                target_allows_overflow=True,
                automation="when-all-spell-slots-empty",
                priority=20 - spell_level,
                source="D&D Basic Rules 2014: Sorcerer, Font of Magic",
            ))
            actions.append(ResourceConversionAction(
                id=f"convert-spell-slot-{spell_level}",
                name=f"Font of Magic: Convert {spell_level}{'st' if spell_level == 1 else 'nd' if spell_level == 2 else 'rd' if spell_level == 3 else 'th'}-Level Spell Slot",
                action_cost="bonus_action",
                source_resource_id=f"spell-slot-{spell_level}",
                source_cost=1,
                target_resource_id="sorcery-points",
                target_gain=spell_level,
                target_allows_overflow=False,
                automation="manual",
                priority=0,
                source="D&D Basic Rules 2014: Sorcerer, Font of Magic",
            ))
        return actions
    except Exception:
        logger.exception("Failed to build 2014 Font of Magic actions for level %s.", level)
        raise


def font_of_magic_2014_level2_actions() -> list[ResourceConversionAction]:
    """Compatibility wrapper for the already-certified level-2 surface."""
    try:
        return font_of_magic_2014_actions(2)
    except Exception:
        logger.exception("Failed to build 2014 Font of Magic level-2 conversion actions.")
        raise
