from __future__ import annotations

import logging

from app.content.monster_creature_types import creature_matches_kind
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def excluded_on_hit_condition_target(defender: CombatantState, effect) -> bool:
    """Return whether source-declared creature kind exclusions block the rider."""
    try:
        kinds = [*effect.excluded_creature_types, *effect.excluded_creature_subtypes]
        return any(creature_matches_kind(defender.template, kind) for kind in kinds)
    except Exception:
        logger.exception(
            "Failed to evaluate on-hit condition-save exclusions for %s.",
            defender.template.name,
        )
        raise
