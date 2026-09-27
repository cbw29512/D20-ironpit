from __future__ import annotations

import logging

from app.combat.zero_hp_replacement import consume_instant_death_prevention
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def apply_instant_death(
    state: CombatantState,
    *,
    affected_states: list[CombatantState] | None = None,
) -> str:
    """Apply a non-damage instant-death effect, honoring source-owned prevention."""
    try:
        if state.is_dead or not state.is_alive:
            return "unchanged"
        if consume_instant_death_prevention(state):
            return "instant_death_prevented"
        state.current_hp = 0
        state.is_alive = False
        state.is_dead = True
        state.is_unconscious = False
        state.is_stable = False
        state.active_effect_ids = [effect for effect in state.active_effect_ids if effect != "dodge"]
        if state.concentration is not None:
            from app.combat.concentration import end_concentration_if_incapacitated
            end_concentration_if_incapacitated(state, affected_states)
        return "dead"
    except Exception as exc:
        logger.exception("Instant-death resolution failed for %s.", state.template.name)
        raise RuntimeError("Instant-death effect could not be resolved.") from exc
