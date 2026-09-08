from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.combat.timed_conditions import apply_timed_condition
from app.domain.actions import HitControlEffect
from app.domain.runtime import CombatantState

PRONE_EFFECT_ID = "prone"


def apply_condition_effect(
    target: CombatantState,
    source_id: str,
    source_effect_id: str,
    effect: HitControlEffect,
    *,
    round_number: int | None = None,
    affected_states: list[CombatantState] | None = None,
) -> str | None:
    """Apply one condition using that condition's actual universal lifecycle."""
    condition_id = effect.condition_id
    if condition_id is None or condition_is_immune(target, condition_id):
        return None
    if condition_id == PRONE_EFFECT_ID:
        if PRONE_EFFECT_ID not in target.active_effect_ids:
            target.active_effect_ids.append(PRONE_EFFECT_ID)
        return PRONE_EFFECT_ID
    return apply_timed_condition(
        target,
        condition_id,
        source_id,
        source_effect_id=source_effect_id,
        applied_round=round_number,
        expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
        expiry_timing=effect.expiry_timing,
        repeat_save_ability=effect.repeat_save_ability,
        repeat_save_dc=effect.repeat_save_dc,
        repeat_save_timing=effect.repeat_save_timing,
        allowed_removal_action_ids=effect.allowed_removal_action_ids,
        affected_states=affected_states,
    )
