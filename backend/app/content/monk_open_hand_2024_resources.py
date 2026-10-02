from __future__ import annotations

import logging

from app.content.monk_2024_resource_rules import monk_focus_points
from app.domain.initiative_resources import InitiativeHealingRider, InitiativeResourceRefillGrant
from app.domain.models import ResourceDefinition

logger = logging.getLogger(__name__)


def build_monk_resources(level: int) -> list[ResourceDefinition]:
    try:
        if level < 2:
            return []
        resources = [
            ResourceDefinition(id="focus-points", name="Focus Points", max_uses=monk_focus_points(level)),
            ResourceDefinition(id="uncanny-metabolism", name="Uncanny Metabolism", max_uses=1),
        ]
        if level >= 6:
            resources.append(ResourceDefinition(
                id="wholeness-of-body",
                name="Wholeness of Body",
                max_uses=1,
            ))
        return resources
    except Exception:
        logger.exception("Failed to build 2024 Monk resources at level %s.", level)
        raise


def build_monk_initiative_refills(level: int) -> list[InitiativeResourceRefillGrant]:
    try:
        if level < 2:
            return []
        return [
            InitiativeResourceRefillGrant(
                source_id="uncanny-metabolism",
                source_name="Uncanny Metabolism",
                resource_id="focus-points",
                when_at_or_below=monk_focus_points(level) - 1,
                restore_to_max=True,
                usage_resource_id="uncanny-metabolism",
                usage_resource_cost=1,
                healing_rider=InitiativeHealingRider(
                    dice_count=1,
                    dice_size=6,
                    healing_bonus=level,
                ),
            )
        ]
    except Exception:
        logger.exception("Failed to build 2024 Monk initiative refills at level %s.", level)
        raise
