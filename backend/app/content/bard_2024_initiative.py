from __future__ import annotations

import logging

from app.domain.initiative_resources import InitiativeResourceRefillGrant

logger = logging.getLogger(__name__)


def build_bard_2024_initiative_refills(level: int) -> list[InitiativeResourceRefillGrant]:
    """Bind 2024 Superior Inspiration to the universal initiative refill primitive."""
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Bard initiative refills cover levels 1 through 20.")
        grants: list[InitiativeResourceRefillGrant] = []
        if level >= 18:
            grants.append(InitiativeResourceRefillGrant(
                source_id="superior-inspiration",
                source_name="Superior Inspiration",
                resource_id="bardic-inspiration",
                when_at_or_below=1,
                restore_to_minimum=2,
            ))
        if level >= 19:
            grants.append(InitiativeResourceRefillGrant(
                source_id="boon-of-fate",
                source_name="Boon of Fate",
                resource_id="boon-of-fate",
                when_at_or_below=0,
                restore_to_max=True,
            ))
        return grants
    except Exception:
        logger.exception("Failed to build 2024 Bard initiative refills at level %s.", level)
        raise
