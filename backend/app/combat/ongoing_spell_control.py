from __future__ import annotations

from app.combat.timed_conditions import apply_timed_condition
from app.domain.actions import AbilityName, ConditionTiming
from app.domain.models import CombatantState


def apply_ongoing_spell_condition(
    target: CombatantState,
    condition_id: str,
    source_id: str,
    spell_id: str,
    save_ability: AbilityName,
    save_dc: int,
    *,
    applied_round: int,
    expiry_timing: ConditionTiming | None = None,
    allowed_removal_action_ids: list[str] | None = None,
    affected_states: list[CombatantState] | None = None,
) -> str | None:
    """Apply an ongoing harmful spell condition with Iron Pit's end-of-turn repeat-save house rule."""
    if not spell_id:
        raise ValueError("Ongoing spell control requires a spell id.")
    if save_dc < 1:
        raise ValueError("Ongoing spell control requires a valid save DC.")
    return apply_timed_condition(
        target,
        condition_id,
        source_id,
        source_effect_id=spell_id,
        applied_round=applied_round,
        expires_at_start_of_source_turn=False,
        expiry_timing=expiry_timing,
        repeat_save_ability=save_ability,
        repeat_save_dc=save_dc,
        repeat_save_timing="target_turn_end",
        allowed_removal_action_ids=allowed_removal_action_ids,
        affected_states=affected_states,
    )
