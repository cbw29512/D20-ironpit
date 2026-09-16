from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)
_DODGE_EFFECT_ID = "dodge"
_PRONE_EFFECT_ID = "prone"


def stabilize_at_zero(state: CombatantState) -> str:
    """Force a source-declared stable 0-HP state after ordinary damage resolution."""
    try:
        state.current_hp = 0
        state.is_alive = True
        state.is_dead = False
        state.is_unconscious = True
        state.is_stable = True
        state.death_save_successes = 0
        state.death_save_failures = 0
        state.active_effect_ids = [
            effect for effect in state.active_effect_ids if effect != _DODGE_EFFECT_ID
        ]
        if (
            not condition_is_immune(state, _PRONE_EFFECT_ID)
            and _PRONE_EFFECT_ID not in state.active_effect_ids
        ):
            state.active_effect_ids.append(_PRONE_EFFECT_ID)
        return "unconscious"
    except Exception as exc:
        logger.exception("Failed to stabilize %s at 0 HP.", state.template.name)
        raise RuntimeError("Zero-HP stabilization could not be resolved.") from exc
