from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def _max_attacks_per_turn(state: CombatantState) -> int | None:
    limits = [
        effect.control_limits.max_attacks_per_turn
        for effect in state.timed_effects
        if effect.control_limits is not None and effect.control_limits.max_attacks_per_turn is not None
    ]
    return min(limits) if limits else None


def turn_attack_allowed(state: CombatantState, *, off_turn: bool = False) -> bool:
    """Return whether another on-turn attack may start under active timed caps."""
    try:
        if off_turn:
            return True
        cap = _max_attacks_per_turn(state)
        if cap is None:
            return True
        return state.attacks_this_turn < cap
    except Exception:
        logger.exception("Failed to resolve timed attack cap for %s.", state.template.name)
        raise


def register_turn_attack(state: CombatantState, *, off_turn: bool = False) -> None:
    """Count one on-turn attack; fail closed if a timed cap is already spent."""
    try:
        if off_turn:
            return
        if not turn_attack_allowed(state, off_turn=False):
            raise ValueError(f"{state.template.name} cannot make another attack this turn.")
        state.attacks_this_turn += 1
    except Exception:
        logger.exception("Failed to register a timed-capped attack for %s.", state.template.name)
        raise
