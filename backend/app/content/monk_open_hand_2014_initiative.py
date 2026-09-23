from __future__ import annotations

import logging

from app.domain.initiative_resources import InitiativeResourceRefillGrant

logger = logging.getLogger(__name__)


def build_monk_2014_initiative_refills(
    level: int,
) -> list[InitiativeResourceRefillGrant]:
    try:
        if level < 20:
            return []
        return [InitiativeResourceRefillGrant(
            source_id="perfect-self",
            source_name="Perfect Self",
            resource_id="ki",
            when_at_or_below=0,
            restore_amount=4,
        )]
    except Exception:
        logger.exception("Failed to build 2014 Monk initiative refills at level %s.", level)
        raise
