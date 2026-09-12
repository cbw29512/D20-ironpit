from __future__ import annotations

from app.combat.source_effect_immunity import (
    grant_source_effect_immunity,
    source_effect_is_immune,
)
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant
from app.domain.models import CombatantState, SavingThrowAction


def target_is_source_effect_immune(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
) -> bool:
    return source_effect_is_immune(target.state, actor.combatant_id, action.id)


def apply_save_control_outcome(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    *,
    succeeded: bool,
    round_number: int,
    affected_states: list[CombatantState] | None = None,
) -> list[str]:
    if succeeded:
        if action.source_effect_immunity_on_success:
            grant_source_effect_immunity(target.state, actor.combatant_id, action.id)
        return []
    control = action.failure_control_effect
    if control is None or control.condition_id is None:
        return []
    expires_round = (
        round_number + control.duration_rounds
        if control.duration_rounds is not None else None
    )
    applied = apply_timed_condition(
        target.state,
        control.condition_id,
        actor.combatant_id,
        source_effect_id=action.id,
        applied_round=round_number,
        expires_round=expires_round,
        expires_at_start_of_source_turn=control.expires_at_start_of_source_turn,
        expiry_timing=control.expiry_timing,
        repeat_save_ability=control.repeat_save_ability,
        repeat_save_dc=control.repeat_save_dc,
        repeat_save_timing=control.repeat_save_timing,
        allowed_removal_action_ids=control.allowed_removal_action_ids,
        affected_states=affected_states,
        source_effect_immunity_on_end=control.source_effect_immunity_on_end,
    )
    return [applied] if applied is not None else []
