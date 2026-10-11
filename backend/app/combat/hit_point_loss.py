from __future__ import annotations

import logging

from app.combat.zero_hp import reduce_to_zero_hit_points
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def lose_hit_points(
    state: CombatantState,
    amount: int,
    *,
    dice=None,
    affected_states: list[CombatantState] | None = None,
) -> int:
    """Lose actual HP, without damage typing, Temp HP, or damage-triggered effects."""
    try:
        if amount < 0:
            raise ValueError("Direct hit point loss cannot be negative.")
        if amount == 0 or state.is_dead or state.current_hp <= 0:
            return 0
        hp_before = state.current_hp
        if amount < hp_before:
            state.current_hp -= amount
        else:
            reduce_to_zero_hit_points(state, dice=dice, affected_states=affected_states)
        return max(0, hp_before - state.current_hp)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Direct HP-loss resolution failed for %s.", state.template.name)
        raise RuntimeError("Direct hit point loss could not be resolved.") from exc
