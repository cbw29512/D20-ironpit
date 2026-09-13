from __future__ import annotations

import logging

from app.combat.hit_points import effective_max_hp
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def apply_max_hp_reduction(state: CombatantState, amount: int) -> tuple[int, int]:
    """Reduce a combatant's temporary combat HP maximum and clamp current HP to the new maximum."""
    try:
        if amount < 0:
            raise ValueError("Maximum HP reduction cannot be negative.")
        before = effective_max_hp(state)
        if amount == 0 or before == 0:
            return before, before
        state.max_hp_reduction += amount
        after = effective_max_hp(state)
        state.current_hp = min(state.current_hp, after)
        return before, after
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Failed to reduce maximum HP for %s.", state.template.name)
        raise RuntimeError("Maximum HP reduction could not be applied.") from exc
