from __future__ import annotations

from app.combat.concentration import end_concentration_if_incapacitated
from app.combat.condition_immunity import condition_is_immune
from app.domain.actions import AbilityName, ConditionTiming
from app.domain.models import BattleEvent, CombatantState, EncounterCombatant, EncounterSetup, TimedEffect


def apply_timed_condition(
    state: CombatantState,
    effect_id: str,
    source_id: str,
    *,
    source_effect_id: str | None = None,
    applied_round: int | None = None,
    expires_at_start_of_source_turn: bool = True,
    expiry_timing: ConditionTiming | None = None,
    repeat_save_ability: AbilityName | None = None,
    repeat_save_dc: int | None = None,
    repeat_save_timing: ConditionTiming | None = None,
    allowed_removal_action_ids: list[str] | None = None,
    affected_states: list[CombatantState] | None = None,
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
        expires_at_start_of_source_turn=expires_at_start_of_source_turn,
        expiry_timing=expiry_timing,
        repeat_save_ability=repeat_save_ability,
        repeat_save_dc=repeat_save_dc,
        repeat_save_timing=repeat_save_timing,
        allowed_removal_action_ids=allowed_removal_action_ids or [],
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
            if effect.source_id == source.combatant_id
            and (effect.expiry_timing == "source_turn_start" or effect.expires_at_start_of_source_turn)
        ]
        for effect in expiring:
            removed = remove_effect_instance(target.state, effect)
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
                removed_condition_ids=[effect.effect_id],
                feature_id="condition-ended",
                animation="condition-ended",
                description=f"{target.state.template.name} is no longer {effect.effect_id.title()}.",
            ))
            sequence += 1
    return events, sequence
