from __future__ import annotations

import logging

from app.domain.actions import HealingAction

logger = logging.getLogger(__name__)


def mass_cure_wounds_2014(
    spellcasting_modifier: int,
    slot_level: int = 5,
    *,
    additional_healing_bonus: int = 0,
) -> HealingAction:
    """Build source-neutral 2014 Mass Cure Wounds on generic group healing."""
    try:
        if not 5 <= slot_level <= 9:
            raise ValueError("2014 Mass Cure Wounds slot level must be between 5 and 9.")
        suffix = "" if slot_level == 5 else f"-l{slot_level}"
        ordinal = {6: "6th", 7: "7th", 8: "8th", 9: "9th"}.get(slot_level)
        name = "Mass Cure Wounds" if slot_level == 5 else f"Mass Cure Wounds ({ordinal}-Level)"
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
            healing_bonus=spellcasting_modifier + additional_healing_bonus,
            resource_id=f"spell-slot-{slot_level}",
            resource_cost=1,
            excluded_creature_types=["undead", "construct"],
            animation="healing",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Mass Cure Wounds at slot level %s.", slot_level)
        raise
