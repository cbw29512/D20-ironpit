from __future__ import annotations

import logging

from app.domain.combatants import ResourceDefinition
from app.domain.initiative_resources import InitiativeResourceRefillGrant

logger = logging.getLogger(__name__)

_REFRESH_RESOURCE_ID = "persistent-rage-refresh"


def persistent_rage_resource(features: tuple[str, ...]) -> ResourceDefinition | None:
    try:
        if "persistent-rage" not in features:
            return None
        return ResourceDefinition(
            id=_REFRESH_RESOURCE_ID,
            name="Persistent Rage Refresh",
            max_uses=1,
        )
    except Exception:
        logger.exception("Failed to compile Persistent Rage refresh resource.")
        raise


def persistent_rage_initiative_refills(
    *,
    rage_uses: int,
    features: tuple[str, ...],
) -> list[InitiativeResourceRefillGrant]:
    try:
        if "persistent-rage" not in features:
            return []
        if rage_uses < 1:
            raise ValueError("Persistent Rage requires a positive finite Rage maximum.")
        return [
            InitiativeResourceRefillGrant(
                source_id="persistent-rage",
                source_name="Persistent Rage",
                resource_id="rage",
                when_at_or_below=rage_uses - 1,
                restore_to_max=True,
                usage_resource_id=_REFRESH_RESOURCE_ID,
                usage_resource_cost=1,
            )
        ]
    except Exception:
        logger.exception(
            "Failed to compile Persistent Rage initiative refill with %s Rage uses.",
            rage_uses,
        )
        raise
