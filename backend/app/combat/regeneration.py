from __future__ import annotations

import logging

from app.combat.hit_points import effective_max_hp
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def regeneration_defers_death(state: CombatantState) -> bool:
    rule = state.template.regeneration
    return bool(rule and rule.dies_at_start_turn_if_zero_and_suppressed)


def resolve_start_turn_regeneration(state: CombatantState) -> tuple[int, bool]:
    """Resolve regeneration before normal turn actions; returns (healed, died)."""
    try:
        rule = state.template.regeneration
        if rule is None or state.is_dead:
            state.damage_types_since_last_turn.clear()
            return 0, False
        suppressed = any(kind in rule.suppressed_by_damage_types for kind in state.damage_types_since_last_turn)
        state.damage_types_since_last_turn.clear()
        if suppressed:
            if rule.dies_at_start_turn_if_zero_and_suppressed and state.current_hp <= 0:
                state.is_alive = False
                state.is_dead = True
                return 0, True
            return 0, False
        before = state.current_hp
        state.current_hp = min(effective_max_hp(state), state.current_hp + rule.hit_points)
        if state.current_hp > 0:
            state.is_alive = True
            state.is_dead = False
        return state.current_hp - before, False
    except Exception as exc:
        logger.exception("Regeneration failed for %s.", state.template.name)
        raise RuntimeError("Regeneration could not be resolved.") from exc
