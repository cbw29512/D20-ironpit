from __future__ import annotations

import logging

from app.combat.debuff_counters import movement_counter_cost
from app.combat.timed_condition_apply import (
    ARENA_POISON_RECOVERY_DC,
    POISONED_EFFECT_ID,
    TERMINAL_CONDITIONS,
    apply_terminal_condition_outcome,
    apply_timed_condition,
)
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def resolve_movement_countered_conditions(
    state: CombatantState,
) -> list[tuple[str, str, int]]:
    """Automatically spend movement to clear active debuffs when a buff grants that option."""
    try:
        from app.combat.flight_ground_immunity import (
            resolve_flight_countered_ground_conditions,
        )

        resolved: list[tuple[str, str, int]] = list(
            resolve_flight_countered_ground_conditions(state)
        )
        for effect in list(state.timed_effects):
            cost = movement_counter_cost(
                state,
                effect.effect_id,
                source_is_magical=effect.source_is_magical,
            )
            if cost is None or state.movement_remaining_ft < cost:
                continue
            removed = remove_effect_group(state, effect)
            if not removed:
                continue
            state.movement_remaining_ft -= cost
            for condition_id in removed:
                resolved.append((condition_id, effect.source_id, cost))
        return resolved
    except Exception:
        logger.exception(
            "Failed to resolve movement-countered conditions for %s.",
            state.template.name,
        )
        raise
