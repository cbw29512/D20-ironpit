from __future__ import annotations

import logging

from app.combat.zero_hp import restore_hit_points
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def apply_survivor_start_turn_heal(state: CombatantState) -> int:
    """Apply universal start-turn healing while alive and at or below half Hit Points."""
    try:
        features = state.template.progression_features
        amount = features.bloodied_start_turn_heal_amount or features.survivor_heal_amount
        if amount <= 0 or state.current_hp <= 0:
            return 0
        maximum = state.template.max_hp + state.max_hp_bonus
        if state.current_hp * 2 > maximum:
            return 0
        return restore_hit_points(state, amount)
    except Exception:
        logger.exception("Failed Survivor start-turn healing for %s", state.template.name)
        raise
