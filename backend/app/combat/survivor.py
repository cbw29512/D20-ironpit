from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def apply_survivor_start_turn_heal(state: CombatantState) -> int:
    """Apply start-turn healing when a compiled Survivor-style feature is active."""
    try:
        amount = state.template.progression_features.survivor_heal_amount
        if amount <= 0 or state.current_hp <= 0:
            return 0
        maximum = state.template.max_hp + state.max_hp_bonus
        if state.current_hp * 2 > maximum:
            return 0
        before = state.current_hp
        state.current_hp = min(maximum, state.current_hp + amount)
        return state.current_hp - before
    except Exception:
        logger.exception("Failed Survivor start-turn healing for %s", state.template.name)
        raise
