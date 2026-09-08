from __future__ import annotations

from app.combat.concentration import end_concentration_if_incapacitated
from app.combat.condition_immunity import condition_is_immune
from app.domain.actions import AbilityName, ConditionTiming
from app.domain.models import BattleEvent, CombatantState, EncounterCombatant, EncounterSetup, TimedEffect
from app.domain.runtime import TimedTurnBehavior


def apply_timed_condition(
    state: CombatantState,
    effect_id: str,
    source_id: str,
    *,
    source_effect_id: str | None = None,
    applied_round: int | None = None,
    expires_round: int | None = None,
    expires_at_start_of_source_turn: bool = True,
    expiry_timing: ConditionTiming | None = None,
    repeat_save_ability: AbilityName | None = None,
    repeat_save_dc: int | None = None,
    repeat_save_timing: ConditionTiming | None = None,
    allowed_removal_action_ids: list[str] | None = None,
    affected_states: list[CombatantState] | None = None,
    turn_behavior: TimedTurnBehavior = "normal",
    ends_on_damage: bool = False,
    ends_if_source_incapacitated: bool = False,
    ends_if_source_dead: bool = False,
) -> str | None:
    if condition_is_immune(state, effect_id):
        return None
    state.timed_effects = [
        effect for effect in state.timed_effects
        if not (
            effect.effect_id == effect_id
            and effect.source_id == source_id
            and effect.source_effect_id == source_effect_id
        )
    ]
    state.timed_effects.append(TimedEffect(
        effect_id=effect_id,
        source_id=source_id,
        source_effect_id=source_effect_id,
        applied_round=applied_round,
        expires_round=expires_round,
        expires_at_start_of_source_turn=expires_at_start_of_source_turn,
        expiry_timing=expiry_timing,
        repeat_save_ability=repeat_save_ability,
        repeat_save_dc=repeat_save_dc,
        repeat_save_timing=repeat_save_timing,
        allowed_removal_action_ids=allowed_removal_action_ids or [],
        turn_behavior=turn_behavior,
        ends_on_damage=ends_on_damage,
        ends_if_source_incapacitated=ends_if_source_incapacitated,
        ends_if_source_dead=ends_if_source_dead,
    ))
    if effect_id not in state.active_effect_ids:
        state.active_effect_ids.append(effect_id)
    end_concentration_if_incapacitated(state, affected_states)
    return effect_id


def remove_effect_instance(state: CombatantState, effect: TimedEffect) -> bool:
    state.timed_effects = [item for item in state.timed_effects if item != effect]
    still_active = any(item.effect_id == effect.effect_id for item in state.timed_effects)
    if not still_active and effect.effect_id in state.active_effect_ids:
        state.active_effect_ids.remove(effect.effect_id)
        return True
    return not still_active


def remove_effect_group(state: CombatantState, effect: TimedEffect) -> list[str]:
    if effect.source_effect_id is None:
        return [effect.effect_id] if remove_effect_instance(state, effect) else []
    grouped = [
        item for item in list(state.timed_effects)
        if item.source_id == effect.source_id and item.source_effect_id == effect.source_effect_id
    ]
    removed: list[str] = []
    for item in grouped:
        if remove_effect_instance(state, item):
            removed.append(item.effect_id)
    return removed
