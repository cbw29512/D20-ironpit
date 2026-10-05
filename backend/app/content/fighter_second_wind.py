from __future__ import annotations

import logging

from app.domain.healing_actions import HealingAction

logger = logging.getLogger(__name__)


def second_wind_healing_action(level: int) -> HealingAction:
    """Compile edition-neutral Second Wind parameters into the shared healing action schema."""
    try:
        if level not in range(1, 21):
            raise ValueError("Second Wind level must be between 1 and 20.")
        return HealingAction(
            id="second-wind",
            name="Second Wind",
            action_cost="bonus_action",
            range_ft=0,
            target_mode="self",
            dice_count=1,
            dice_size=10,
            healing_bonus=level,
            resource_id="second-wind",
            resource_cost=1,
            animation="second-wind",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to compile Second Wind healing action at level %s.", level)
        raise RuntimeError("Second Wind healing action could not be compiled.") from exc
