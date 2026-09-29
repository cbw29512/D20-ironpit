from __future__ import annotations

import logging

from app.content.bard_combat_levels import BARD_COMBAT_LEVELS
from app.domain.resource_conversion import ResourceConversionAction

logger = logging.getLogger(__name__)


def build_font_of_inspiration_2024(level: int) -> list[ResourceConversionAction]:
    """Spend any available spell slot, no action required, to restore one Bardic Inspiration."""
    try:
        if not 5 <= level <= 20:
            raise ValueError("2024 Font of Inspiration requires Bard level 5 or higher.")
        row = BARD_COMBAT_LEVELS[level]
        actions: list[ResourceConversionAction] = []
        for spell_level, uses in enumerate(row.spell_slots, start=1):
            if not uses:
                continue
            actions.append(ResourceConversionAction(
                id=f"font-of-inspiration-slot-{spell_level}",
                name=f"Font of Inspiration ({spell_level}{'st' if spell_level == 1 else 'nd' if spell_level == 2 else 'rd' if spell_level == 3 else 'th'}-Level Slot)",
                action_cost="none",
                source_resource_id=f"spell-slot-{spell_level}",
                source_cost=1,
                target_resource_id="bardic-inspiration",
                target_gain=1,
                target_allows_overflow=False,
                automation="manual",
                priority=100 - spell_level,
                source="D&D Beyond Basic Rules 2024: Bard 5, Font of Inspiration",
            ))
        return actions
    except Exception:
        logger.exception("Failed to build 2024 Font of Inspiration at level %s.", level)
        raise
