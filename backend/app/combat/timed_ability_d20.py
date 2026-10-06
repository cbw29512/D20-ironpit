from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def timed_ability_d20_disadvantage_sources(state: CombatantState, ability: str | None) -> int:
    """Count timed riders that impose Disadvantage on one ability's D20 Tests."""
    try:
        if not ability:
            return 0
        wanted = str(ability).strip().casefold()
        if not wanted:
            return 0
        return sum(
            1
            for effect in state.timed_effects
            if effect.control_limits is not None
            and wanted in effect.control_limits.d20_disadvantage_abilities
        )
    except Exception:
        logger.exception(
            "Failed to resolve timed ability D20 Disadvantage for %s / %s.",
            state.template.name,
            ability,
        )
        raise
