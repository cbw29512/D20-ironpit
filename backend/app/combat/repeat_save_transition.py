from __future__ import annotations

from app.combat.timed_conditions import apply_timed_condition, remove_effect_group
from app.domain.models import CombatantState, TimedEffect


def resolve_repeat_save_transition(
    state: CombatantState, effect: TimedEffect, succeeded: bool, round_number: int,
) -> tuple[list[str], list[str]]:
    """End an effect on success or replace it with its configured escalation on failure."""
    if succeeded:
        return remove_effect_group(state, effect), []
    if effect.repeat_save_failure_condition is None:
        return [], []
    removed = remove_effect_group(state, effect)
    escalated = apply_timed_condition(
        state,
        effect.repeat_save_failure_condition,
        effect.source_id,
        source_effect_id=effect.source_effect_id,
        applied_round=round_number,
    )
    return removed, [escalated] if escalated is not None else []
