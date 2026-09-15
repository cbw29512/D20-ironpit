from __future__ import annotations

from app.combat.auras import resolve_start_turn_auras
from app.combat.condition_rules import BLINDED, is_incapacitated, has_condition
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.start_turn_damage import resolve_start_turn_relationship_damage
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def _opponents(actor: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    return setup.monsters if actor.side == "heroes" else setup.heroes


def _mutual_sight(actor: EncounterCombatant, source: EncounterCombatant) -> bool:
    return not has_condition(actor.state, BLINDED) and not has_condition(source.state, BLINDED)


def _apply_failure(actor, source, gaze, round_number: int, roll, affected_states) -> str | None:
    immediate = (
        gaze.immediate_failure_margin is not None
        and gaze.immediate_failure_condition_id is not None
        and roll is not None
        and roll.total <= gaze.save_dc - gaze.immediate_failure_margin
    )
    if immediate:
        return apply_timed_condition(
            actor.state, gaze.immediate_failure_condition_id, source.combatant_id,
            source_effect_id=gaze.id, applied_round=round_number,
            expires_at_start_of_source_turn=False, affected_states=affected_states,
        )
    return apply_timed_condition(
        actor.state, gaze.failure_condition_id, source.combatant_id,
        source_effect_id=gaze.id, applied_round=round_number,
        expires_at_start_of_source_turn=False,
        repeat_save_ability=gaze.save_ability, repeat_save_dc=gaze.save_dc,
        repeat_save_timing=gaze.repeat_save_timing,
        repeat_save_failure_condition_id=gaze.repeat_save_failure_condition_id,
        affected_states=affected_states,
    )


def resolve_start_turn_gazes(
    sequence: int, round_number: int, actor: EncounterCombatant, setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int]:
    events, sequence = resolve_start_turn_relationship_damage(sequence, round_number, actor, setup, dice)
    aura_events, sequence = resolve_start_turn_auras(sequence, round_number, actor, setup, dice)
    events.extend(aura_events)
    affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
    for source in _opponents(actor, setup):
        gaze = source.state.template.start_turn_gaze
        if gaze is None or is_incapacitated(source.state) or is_incapacitated(actor.state):
            continue
        if combatant_distance(actor, source) > gaze.range_ft or not _mutual_sight(actor, source):
            continue
        roll, succeeded = resolve_saving_throw(
            actor.state, gaze.save_ability, gaze.save_dc, dice,
            magical_effect=gaze.magical_effect, against_condition=gaze.failure_condition_id,
        )
        applied = None if succeeded else _apply_failure(actor, source, gaze, round_number, roll, affected_states)
        outcome = "SUCCEEDS" if succeeded else "FAILS"
        description = f"{actor.state.template.name} {outcome} a DC {gaze.save_dc} {gaze.save_ability.title()} save against {source.state.template.name}'s {gaze.name}."
        if applied: description += f" {actor.state.template.name} is {applied.title()}."
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="saving_throw",
            actor_id=source.combatant_id, actor_name=source.state.template.name,
            target_id=actor.combatant_id, target_name=actor.state.template.name,
            saving_throw_roll=roll, save_ability=gaze.save_ability, save_dc=gaze.save_dc,
            save_succeeded=succeeded, applied_condition_ids=[applied] if applied else [],
            feature_id=gaze.id, animation="condition-save", description=description,
        ))
        sequence += 1
        if is_incapacitated(actor.state):
            break
    return events, sequence
