from __future__ import annotations

import logging

from app.domain.actions import HealingAction

logger = logging.getLogger(__name__)


def healing_word_2014(casting_modifier: int) -> HealingAction:
    try:
        return HealingAction(
            id="healing-word", name="Healing Word", action_cost="bonus_action",
            range_ft=60, target_mode="self_or_ally", dice_count=1, dice_size=4,
            healing_bonus=casting_modifier, resource_id="spell-slot-1", resource_cost=1,
            excluded_creature_types=["undead", "construct"], animation="healing",
        )
    except Exception:
        logger.exception("Failed to compile shared 2014 Healing Word.")
        raise


def cure_wounds_2014(casting_modifier: int) -> HealingAction:
    try:
        return HealingAction(
            id="cure-wounds", name="Cure Wounds", action_cost="action",
            range_ft=5, target_mode="self_or_ally", dice_count=1, dice_size=8,
            healing_bonus=casting_modifier, resource_id="spell-slot-1", resource_cost=1,
            excluded_creature_types=["undead", "construct"], animation="healing",
        )
    except Exception:
        logger.exception("Failed to compile shared 2014 Cure Wounds.")
        raise
