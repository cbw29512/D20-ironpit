from __future__ import annotations

import logging

from app.domain.actions import HealingAction

logger = logging.getLogger(__name__)


def divine_intervention_full_heal_2014(level: int) -> HealingAction:
    """2014 Divine Intervention using Iron Pit's deterministic full-heal policy."""
    try:
        if not 10 <= level <= 20:
            raise ValueError("2014 Divine Intervention requires Cleric level 10 or higher.")
        return HealingAction(
            id="divine-intervention",
            name="Divine Intervention",
            action_cost="action",
            range_ft=120,
            target_mode="self_or_ally",
            max_targets=1,
            restore_to_effective_max=True,
            percentile_success_max=None if level >= 20 else level,
            resource_id="divine-intervention",
            resource_cost=1,
            animation="divine-intervention",
        )
    except Exception:
        logger.exception("Failed to build 2014 Divine Intervention at level %s.", level)
        raise
