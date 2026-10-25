from __future__ import annotations

import logging

from app.combat.timed_conditions import apply_timed_condition
from app.domain.combatants import CombatantTemplate
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


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
) -> str | None:
    """Apply match-scoped source immunity. Discarded when the fight instance resets."""
    try:
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
            expires_round=None,
            expiry_timing=None,
            expires_at_start_of_source_turn=False,
            use_default_poison_recovery=False,
        )
    except Exception:
        logger.exception(
            "Failed to grant source-effect immunity for %s from %s.",
            action_id,
            source_id,
        )
        raise


def shared_immunity_effect_id(key: str) -> str:
    try:
        normalized = key.strip().casefold()
        if not normalized:
            raise ValueError("Shared immunity key must be nonblank.")
        return f"shared-save-immunity:{normalized}"
    except Exception:
        logger.exception("Failed to normalize shared save-immunity key %r.", key)
        raise


def has_shared_source_effect_immunity(state: CombatantState, keys: list[str]) -> bool:
    try:
        wanted = {shared_immunity_effect_id(key) for key in keys}
        return any(effect.effect_id in wanted for effect in state.timed_effects)
    except Exception:
        logger.exception("Failed shared source-effect immunity lookup for keys %s.", keys)
        raise


def grant_shared_source_effect_immunities(
    state: CombatantState,
    keys: list[str],
    source_id: str,
    round_number: int,
    *,
    source_template: CombatantTemplate | None = None,
    source_is_magical: bool = False,
) -> list[str]:
    try:
        applied: list[str] = []
        for key in keys:
            effect_id = shared_immunity_effect_id(key)
            if any(effect.effect_id == effect_id for effect in state.timed_effects):
                applied.append(effect_id)
                continue
            result = apply_timed_condition(
                state, effect_id, source_id,
                source_effect_id="shared-save-immunity",
                source_template=source_template,
                source_is_magical=source_is_magical,
                applied_round=round_number,
                expires_round=None,
                expiry_timing=None,
                expires_at_start_of_source_turn=False,
                use_default_poison_recovery=False,
            )
            if result is not None:
                applied.append(result)
        return applied
    except Exception:
        logger.exception("Failed to grant shared source-effect immunities for %s.", keys)
        raise
