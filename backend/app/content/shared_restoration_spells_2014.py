from __future__ import annotations

import logging

from app.domain.actions import ConditionRemovalAction

logger = logging.getLogger(__name__)


def greater_restoration_2014() -> ConditionRemovalAction:
    """Build 2014 Greater Restoration for the charm/petrify subset the engine can resolve.

    D&D Basic Rules 2014 / SRD 5.1 Greater Restoration also reduces exhaustion by one
    level and can end one curse, one ability-score reduction, or one hit-point-maximum
    reduction. Those riders have no matching primitive and stay fail-closed.
    """
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
            animation="greater-restoration",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Greater Restoration.")
        raise
