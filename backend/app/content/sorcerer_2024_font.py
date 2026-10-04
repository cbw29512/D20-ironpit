from __future__ import annotations

import logging

from app.content.sorcerer_combat_levels import SORCERER_COMBAT_LEVELS
from app.domain.resource_conversion import ResourceConversionAction

logger = logging.getLogger(__name__)

_SLOT_CREATION_COST = {1: 2, 2: 3, 3: 5, 4: 6, 5: 7}
_MIN_LEVEL_TO_CREATE = {1: 2, 2: 3, 3: 5, 4: 7, 5: 9}


def font_of_magic_2024_actions(level: int) -> list[ResourceConversionAction]:
    """2024 Font of Magic: slot-to-points is no action; creating a slot is a Bonus Action."""
    try:
        if not 2 <= level <= 20:
            raise ValueError("2024 Font of Magic requires Sorcerer level 2 or higher.")
        row = SORCERER_COMBAT_LEVELS[level]
        highest_slot = max(
            (spell_level for spell_level, uses in enumerate(row.spell_slots, start=1) if uses),
            default=0,
        )
        actions: list[ResourceConversionAction] = []
        for spell_level in range(1, min(5, highest_slot) + 1):
            ordinal = {1: "st", 2: "nd", 3: "rd"}.get(spell_level, "th")
            actions.append(ResourceConversionAction(
                id=f"convert-spell-slot-{spell_level}",
                name=f"Font of Magic: Convert {spell_level}{ordinal}-Level Spell Slot",
                action_cost="none",
                source_resource_id=f"spell-slot-{spell_level}",
                source_cost=1,
                target_resource_id="sorcery-points",
                target_gain=spell_level,
                target_allows_overflow=False,
                automation="manual",
                priority=0,
                source="D&D Beyond Basic Rules 2024: Sorcerer, Font of Magic",
            ))
            if level >= _MIN_LEVEL_TO_CREATE[spell_level]:
                actions.append(ResourceConversionAction(
                    id=f"create-spell-slot-{spell_level}",
                    name=f"Font of Magic: Create {spell_level}{ordinal}-Level Spell Slot",
                    action_cost="bonus_action",
                    source_resource_id="sorcery-points",
                    source_cost=_SLOT_CREATION_COST[spell_level],
                    target_resource_id=f"spell-slot-{spell_level}",
                    target_gain=1,
                    target_allows_overflow=True,
                    automation="when-all-spell-slots-empty",
                    priority=20 - spell_level,
                    source="D&D Beyond Basic Rules 2024: Sorcerer, Font of Magic",
                ))
        return actions
    except Exception:
        logger.exception("Failed to build 2024 Font of Magic actions for level %s.", level)
        raise
