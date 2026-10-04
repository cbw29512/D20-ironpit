from __future__ import annotations

import logging

from app.domain.teleport_actions import TeleportAction

logger = logging.getLogger(__name__)


def dimension_door_2014() -> TeleportAction:
    """Build 2014 Dimension Door: 500-foot teleport with one willing passenger within 5 feet."""
    try:
        return TeleportAction(
            id="dimension-door",
            name="Dimension Door",
            level=4,
            action_cost="action",
            range_ft=500,
            passenger_count=1,
            passenger_range_ft=5,
            resource_id="spell-slot-4",
            expends_spell_slot=True,
            animation="dimension-door",
            source="D&D Basic Rules 2014 / SRD 5.1: Dimension Door",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Dimension Door.")
        raise
