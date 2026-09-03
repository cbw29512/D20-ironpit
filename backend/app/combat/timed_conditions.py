from __future__ import annotations

from app.combat.concentration import end_concentration_if_incapacitated
from app.combat.condition_immunity import condition_is_immune
from app.domain.actions import AbilityName, ConditionTiming
from app.domain.models import BattleEvent, CombatantState, EncounterCombatant, EncounterSetup, TimedEffect
from app.domain.runtime import TimedTurnBehavior

POISONED_EFFECT_ID = "poisoned"
ARENA_POISON_RECOVERY_DC = 10


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
    if effect_id == POISONED_EFFECT_ID:
        if any(effect.effect_id == POISONED_EFFECT_ID for effect in state.timed_effects):
            return POISONED_EFFECT_ID
        expires_at_start_of_source_turn = False
        expiry_timing = None
        repeat_save_ability = repeat_save_ability or "constitution"
        repeat_save_dc = repeat_save_dc or ARENA_POISON_RECOVERY_DC
        repeat_save_timing = "target_turn_start"
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


def _source_start_expired(effect: TimedEffect, round_number: int) -> bool:
    source_start = effect.expiry_timing == "source_turn_start" or effect.expires_at_start_of_source_turn
    return source_start and (effect.expires_round is None or round_number >= effect.expires_round)


def expire_start_of_turn_conditions(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    for target in [*setup.heroes, *setup.monsters]:
        expiring = [
            effect for effect in target.state.timed_effects
            if effect.source_id == source.combatant_id and _source_start_expired(effect, round_number)
        ]
        for effect in expiring:
            removed = remove_effect_group(target.state, effect)
            if not removed:
                continue
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=source.combatant_id,
                actor_name=source.state.template.name,
                target_id=target.combatant_id,
                target_name=target.state.template.name,
                removed_condition_ids=removed,
                feature_id=effect.source_effect_id or "condition-ended",
                animation="condition-ended",
                description=f"{target.state.template.name} is no longer affected by {effect.source_effect_id or effect.effect_id}.",
            ))
            sequence += 1
    return events, sequence
