"""Untyped direct Hit Point loss: no damage defenses or damage-trigger events."""

import logging

from app.combat.zero_hp import reduce_to_zero_hit_points
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def lose_hit_points(
    state: CombatantState, amount: int, *, dice=None, affected_states=None,
) -> int:
    """Return actual HP lost; hand zero HP to the existing non-damage lifecycle."""
    try:
        if not isinstance(amount, int) or amount < 0:
            raise ValueError("Hit Point loss must be a nonnegative integer.")
        if amount == 0 or state.is_dead or not state.is_alive or state.current_hp <= 0:
            return 0
        before = state.current_hp
        if amount >= before:
            reduce_to_zero_hit_points(state, dice=dice, affected_states=affected_states)
        else:
            state.current_hp -= amount
        return before - state.current_hp
    except (TypeError, ValueError):
        raise
    except Exception:
        logger.exception("Direct Hit Point loss failed for %s.", state.template.name)
        raise
