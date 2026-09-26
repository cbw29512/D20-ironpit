from __future__ import annotations

import logging

from app.domain.initiative_resources import InitiativeResourceRefillGrant

logger = logging.getLogger(__name__)


def build_bard_2014_initiative_refills(level: int) -> list[InitiativeResourceRefillGrant]:
    """Bind 2014 Superior Inspiration to the universal initiative refill primitive."""
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Bard initiative refills cover levels 1 through 20.")
        if level < 20:
            return []
        return [InitiativeResourceRefillGrant(
            source_id="superior-inspiration",
            source_name="Superior Inspiration",
            resource_id="bardic-inspiration",
            when_at_or_below=0,
            restore_amount=1,
        )]
    except Exception:
        logger.exception("Failed to build 2014 Bard initiative refills at level %s.", level)
        raise
