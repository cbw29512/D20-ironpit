from __future__ import annotations

import logging

from app.combat.hit_points import effective_max_hp
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def reduce_max_hp(state: CombatantState, amount: int, *, kill_at_zero: bool = False) -> int:
    """Apply fight-scoped maximum-HP reduction and return the amount actually reduced."""
    try:
        if amount < 0:
            raise ValueError("Maximum-HP reduction cannot be negative.")
        before = effective_max_hp(state)
        reduction = min(amount, before)
        state.max_hp_reduction += reduction
        after = effective_max_hp(state)
        state.current_hp = min(state.current_hp, after)
        if kill_at_zero and after == 0:
            state.current_hp = 0
            state.is_alive = False
            state.is_unconscious = False
            state.is_stable = False
            state.is_dead = True
            state.death_save_successes = 0
            state.death_save_failures = 0
        return reduction
    except Exception:
        logger.exception("Failed to reduce maximum HP for %s.", state.template.name)
        raise
