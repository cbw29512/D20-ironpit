from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def effective_max_hp(state: CombatantState) -> int:
    """Return the current Hit Point maximum after temporary increases and reductions."""
    try:
        return max(0, state.template.max_hp + state.max_hp_bonus - state.max_hp_reduction)
    except Exception:
        logger.exception("Failed to calculate effective Hit Point maximum for %s.", state.template.name)
        raise


def reduce_max_hp(state: CombatantState, amount: int) -> int:
    """Apply a temporary maximum-HP reduction and clamp current HP to the new maximum."""
    try:
        if amount < 0:
            raise ValueError("Hit Point maximum reduction cannot be negative.")
        if amount == 0 or state.is_dead:
            return 0
        before = effective_max_hp(state)
        state.max_hp_reduction += amount
        after = effective_max_hp(state)
        state.current_hp = min(state.current_hp, after)
        if after == 0:
            state.current_hp = 0
            state.is_alive = False
            state.is_dead = True
            state.is_unconscious = False
            state.is_stable = False
        return before - after
    except ValueError:
        raise
    except Exception:
        logger.exception("Failed to reduce Hit Point maximum for %s.", state.template.name)
        raise
