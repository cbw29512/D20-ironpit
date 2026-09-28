from __future__ import annotations

import logging

from app.domain.initiative_resources import InitiativeResourceRefillGrant

logger = logging.getLogger(__name__)


def persistent_rage_initiative_refills(
    *,
    rage_uses: int,
    features: tuple[str, ...],
) -> list[InitiativeResourceRefillGrant]:
    """Bind 2024 Persistent Rage to the universal initiative-refill primitive."""
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
                restore_amount=rage_uses,
            )
        ]
    except Exception:
        logger.exception(
            "Failed to compile Persistent Rage initiative refill with %s Rage uses.",
            rage_uses,
        )
        raise
