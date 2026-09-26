from __future__ import annotations

import logging

from app.domain.resource_conversion import ResourceConversionAction

logger = logging.getLogger(__name__)


def font_of_magic_2014_level2_actions() -> list[ResourceConversionAction]:
    try:
        return [
            ResourceConversionAction(
                id="create-spell-slot-1",
                name="Font of Magic: Create 1st-Level Spell Slot",
                action_cost="bonus_action",
                source_resource_id="sorcery-points",
                source_cost=2,
                target_resource_id="spell-slot-1",
                target_gain=1,
                target_allows_overflow=True,
                automation="when-all-spell-slots-empty",
                priority=10,
                source="D&D Basic Rules 2014: Sorcerer 2, Font of Magic",
            ),
            ResourceConversionAction(
                id="convert-spell-slot-1",
                name="Font of Magic: Convert 1st-Level Spell Slot",
                action_cost="bonus_action",
                source_resource_id="spell-slot-1",
                source_cost=1,
                target_resource_id="sorcery-points",
                target_gain=1,
                target_allows_overflow=False,
                automation="manual",
                priority=0,
                source="D&D Basic Rules 2014: Sorcerer 2, Font of Magic",
            ),
        ]
    except Exception:
        logger.exception("Failed to build 2014 Font of Magic level-2 conversion actions.")
        raise
