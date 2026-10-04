from __future__ import annotations

import logging

from app.domain.actions import ConditionRemovalAction

logger = logging.getLogger(__name__)


def greater_restoration_2024() -> ConditionRemovalAction:
    """2024 Greater Restoration: Action, Touch, end one printed restoration rider."""
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
        logger.exception("Failed to build 2024 Greater Restoration.")
        raise
