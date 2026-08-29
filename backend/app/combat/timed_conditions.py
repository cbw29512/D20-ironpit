from __future__ import annotations

from app.domain.models import BattleEvent, CombatantState, EncounterCombatant, EncounterSetup, TimedEffect


def apply_timed_condition(
    state: CombatantState,
    effect_id: str,
    source_id: str,
    *,
    expires_at_start_of_source_turn: bool = True,
) -> str:
    state.timed_effects = [
        effect for effect in state.timed_effects
        if not (effect.effect_id == effect_id and effect.source_id == source_id)
    ]
    state.timed_effects.append(TimedEffect(
        effect_id=effect_id,
        source_id=source_id,
        expires_at_start_of_source_turn=expires_at_start_of_source_turn,
    ))
    if effect_id not in state.active_effect_ids:
        state.active_effect_ids.append(effect_id)
    return effect_id


def _remove_source_effect(state: CombatantState, effect: TimedEffect) -> bool:
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
            if effect.source_id == source.combatant_id and effect.expires_at_start_of_source_turn
        ]
        for effect in expiring:
            removed = _remove_source_effect(target.state, effect)
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
