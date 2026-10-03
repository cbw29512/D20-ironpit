from __future__ import annotations

import logging

from app.domain.models import ResourceDefinition

logger = logging.getLogger(__name__)


def build_paladin_2024_resources(level: int) -> list[ResourceDefinition]:
    try:
        resources = [
            ResourceDefinition(id="lay-on-hands", name="Lay On Hands", max_uses=5 * level),
            ResourceDefinition(
                id="spell-slot-1",
                name="Level 1 Spell Slot",
                max_uses=4 if level >= 5 else (3 if level >= 3 else 2),
            ),
        ]
        if level >= 2:
            resources.append(ResourceDefinition(
                id="paladins-smite-free-cast",
                name="Paladin's Smite: Free Cast",
                max_uses=1,
            ))
        if level >= 3:
            resources.append(ResourceDefinition(
                id="channel-divinity",
                name="Channel Divinity",
                max_uses=2,
            ))
        if level >= 5:
            resources.extend([
                ResourceDefinition(
                    id="spell-slot-2",
                    name="Level 2 Spell Slot",
                    max_uses=3 if level >= 7 else 2,
                ),
                ResourceDefinition(
                    id="faithful-steed-free-cast",
                    name="Faithful Steed: Free Cast",
                    max_uses=1,
                ),
            ])
        return resources
    except Exception:
        logger.exception("Failed to build 2024 Paladin resources at level %s.", level)
        raise
