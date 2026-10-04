from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def marked_target_advantage_sources(attacker: CombatantState, defender_id: str) -> int:
    """Advantage on attack rolls against the creature currently marked by the declared effect."""
    try:
        effect_id = attacker.template.progression_features.advantage_against_marked_effect_id
        if not effect_id:
            return 0
        return int(any(
            item.source_effect_id == effect_id and item.target_id == defender_id
            for item in attacker.active_modifiers
        ))
    except Exception:
        logger.exception("Marked-target Advantage lookup failed for %s.", attacker.template.name)
        raise
