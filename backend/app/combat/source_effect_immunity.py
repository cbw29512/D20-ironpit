from __future__ import annotations

import logging

from app.combat.timed_conditions import apply_timed_condition
from app.domain.combatants import CombatantTemplate
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)
SOURCE_EFFECT_IMMUNITY_ROUNDS_24H = 24 * 60 * 10


def immunity_effect_id(action_id: str, source_id: str) -> str:
    return f"{action_id}:success-immunity:{source_id}"


def has_source_effect_immunity(state: CombatantState, action_id: str, source_id: str) -> bool:
    try:
        key = immunity_effect_id(action_id, source_id)
        return any(effect.effect_id == key for effect in state.timed_effects)
    except Exception:
        logger.exception(
            "Failed source-effect immunity lookup for %s from %s.",
            action_id,
            source_id,
        )
        raise


def grant_source_effect_immunity(
    state: CombatantState,
    action_id: str,
    source_id: str,
    round_number: int,
    *,
    source_template: CombatantTemplate | None = None,
    source_is_magical: bool = False,
    rounds: int = SOURCE_EFFECT_IMMUNITY_ROUNDS_24H,
) -> str | None:
    """Apply source-specific timed immunity used by Frightful Presence and matching saves."""
    try:
        if rounds <= 0:
            return None
        if has_source_effect_immunity(state, action_id, source_id):
            return immunity_effect_id(action_id, source_id)
        return apply_timed_condition(
            state,
            immunity_effect_id(action_id, source_id),
            source_id,
            source_effect_id=f"{action_id}:success-immunity",
            source_template=source_template,
            source_is_magical=source_is_magical,
            applied_round=round_number,
            expires_round=round_number + rounds,
            expiry_timing="source_turn_start",
            expires_at_start_of_source_turn=True,
            use_default_poison_recovery=False,
        )
    except Exception:
        logger.exception(
            "Failed to grant source-effect immunity for %s from %s.",
            action_id,
            source_id,
        )
        raise
