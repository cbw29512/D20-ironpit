from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def distance_attack_disadvantage_sources(
    attacker: CombatantState,
    distance_ft: int,
) -> int:
    """Return one Disadvantage source when a source-owned threshold is exceeded."""
    try:
        threshold = attacker.template.progression_features.attack_disadvantage_beyond_ft
        return int(threshold > 0 and distance_ft > threshold)
    except Exception:
        logger.exception(
            "Failed to resolve distance attack Disadvantage for %s.",
            attacker.template.name,
        )
        raise
