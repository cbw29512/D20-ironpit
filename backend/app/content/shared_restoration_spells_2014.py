from __future__ import annotations

import logging

from app.domain.actions import ConditionRemovalAction

logger = logging.getLogger(__name__)


def greater_restoration_2014() -> ConditionRemovalAction:
    """Build 2014 Greater Restoration, ending exactly one printed rider."""
    try:
        return ConditionRemovalAction(
            id="greater-restoration",
            name="Greater Restoration",
            action_cost="action",
            range_ft=5,
            target_mode="self_or_ally",
            removable_conditions=["charmed", "petrified"],
            max_conditions_per_use=1,
            resource_costs={"spell-slot-5": 1},
            expends_spell_slot=True,
            reduces_exhaustion_levels=1,
            removes_curses=True,
            removes_ability_score_reductions=True,
            removes_hit_point_maximum_reductions=True,
            animation="greater-restoration",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Greater Restoration.")
        raise


def remove_curse_2014() -> ConditionRemovalAction:
    """Build 2014 Remove Curse, ending every curse on the touched creature."""
    try:
        return ConditionRemovalAction(
            id="remove-curse",
            name="Remove Curse",
            action_cost="action",
            range_ft=5,
            target_mode="self_or_ally",
            removable_conditions=[],
            max_conditions_per_use=1,
            resource_costs={"spell-slot-3": 1},
            expends_spell_slot=True,
            removes_all_curses=True,
            animation="remove-curse",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Remove Curse.")
        raise
