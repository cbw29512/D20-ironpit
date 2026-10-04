from __future__ import annotations

import logging

from app.content.character_resource_rules import expected_resources
from app.content.ranger_hunter_2024_profile import build_rowan_ashtrail_2024_profile
from app.domain.models import ResourceDefinition

logger = logging.getLogger(__name__)
_NAMES = {
    "favored-enemy-hunters-mark": "Favored Enemy: Hunter's Mark",
    "tireless": "Tireless",
    "natures-veil": "Nature's Veil",
    "boon-combat-prowess": "Boon of Combat Prowess",
}


def build_rowan_2024_resources(level: int) -> list[ResourceDefinition]:
    try:
        expected = expected_resources(build_rowan_ashtrail_2024_profile(level))
        resources: list[ResourceDefinition] = []
        for resource_id, uses in expected.items():
            if resource_id.startswith("spell-slot-"):
                name = f"Level {resource_id.removeprefix('spell-slot-')} Spell Slot"
            else:
                name = _NAMES.get(resource_id, resource_id)
            resources.append(ResourceDefinition(id=resource_id, name=name, max_uses=uses))
        return resources
    except Exception:
        logger.exception("Failed to build 2024 Rowan resources at level %s.", level)
        raise
