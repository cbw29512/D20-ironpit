from __future__ import annotations

import logging

from app.domain.actions import HealingAction

logger = logging.getLogger(__name__)


def mass_cure_wounds_2014(
    wisdom_modifier: int,
    slot_level: int = 5,
) -> HealingAction:
    """Compile legacy Mass Cure Wounds onto generic area group healing."""
    try:
        if wisdom_modifier < 0:
            raise ValueError("2014 Mass Cure Wounds requires a nonnegative Wisdom modifier.")
        if not 5 <= slot_level <= 9:
            raise ValueError("2014 Mass Cure Wounds slot level must be between 5 and 9.")
        suffix = "" if slot_level == 5 else f"-l{slot_level}"
        name = "Mass Cure Wounds" if slot_level == 5 else f"Mass Cure Wounds ({slot_level}th-Level)"
        return HealingAction(
            id=f"mass-cure-wounds{suffix}",
            name=name,
            action_cost="action",
            range_ft=60,
            area_radius_ft=30,
            target_mode="self_or_ally",
            max_targets=6,
            dice_count=3 + (slot_level - 5),
            dice_size=8,
            healing_bonus=wisdom_modifier + 2 + slot_level,
            resource_id=f"spell-slot-{slot_level}",
            resource_cost=1,
            excluded_creature_types=["undead", "construct"],
            animation="healing",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Mass Cure Wounds at slot level %s.", slot_level)
        raise
