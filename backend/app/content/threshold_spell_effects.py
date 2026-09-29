from __future__ import annotations

import logging

from app.domain.actions import HpThresholdInstantDeathAction

logger = logging.getLogger(__name__)


def build_power_word_kill_2024() -> HpThresholdInstantDeathAction:
    """2024 Power Word Kill: threshold death, otherwise typed fallback damage."""
    try:
        return HpThresholdInstantDeathAction(
            id="power-word-kill",
            name="Power Word Kill",
            action_cost="action",
            range_ft=60,
            max_current_hp=100,
            fallback_damage_dice_count=12,
            fallback_damage_dice_size=12,
            fallback_damage_type="psychic",
            resource_id="spell-slot-9",
            resource_cost=1,
            magical_effect=True,
            animation="instant-death",
        )
    except Exception:
        logger.exception("Failed to build 2024 Power Word Kill.")
        raise
