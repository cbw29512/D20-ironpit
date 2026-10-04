from __future__ import annotations

import logging

from app.combat.concentration import end_concentration_if_expired
from app.combat.condition_lifecycle import resolve_source_condition_timing, resolve_target_condition_timing
from app.combat.death_saves import resolve_death_save
from app.combat.delayed_resource_refill import resolve_delayed_resource_refill_end_turn
from app.combat.dice import DiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_events import build_encounter_result, build_finish_event, build_initiative_events
from app.combat.exile import resolve_source_exile_returns
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.encounter_outcome import resolve_encounter_outcome
from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import select_nearest_target
from app.combat.hit_modifiers import expire_source_turn_start_modifiers
from app.combat.incoming_damage_resistance import expire_current_turn_type_resistances
from app.combat.start_of_turn_save_condition_events import (
    resolve_start_of_turn_save_condition_damage_events,
)
from app.combat.intimidating_presence_2014 import end_invalid_presence
from app.combat.initiative_resource_refill import resolve_initiative_resource_refills
from app.combat.modifier_stack import expire_source_turn_modifiers
from app.combat.precombat_buffs import prepare_opening_buffs
from app.combat.source_bound_effects import cleanup_disabled_source_effects
from app.combat.start_turn_timed_self_buffs import resolve_start_turn_timed_self_buff
from app.combat.persistent_barrier_lifecycle import cleanup_persistent_barriers
from app.combat.state import refresh_start_of_turn
from app.combat.timed_conditions import expire_start_of_turn_conditions
from app.combat.persistent_save_zone_windows import resolve_save_zone_window
from app.combat.suppression_zone_effects import expire_suppression_zones, sync_suppression_zone_effects
from app.combat.timed_emanations import resolve_target_turn_start_emanations
from app.domain.encounters import EncounterBattleResult, EncounterCombatant, EncounterSelection
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)
MAX_ENCOUNTER_ROUNDS = 100


def _combatant_index(combatants: list[EncounterCombatant]) -> dict[str, EncounterCombatant]:
    return {member.combatant_id: member for member in combatants}


def _resolve_zero_hp_turn(
    sequence: int,
    round_number: int,
    combatant: EncounterCombatant,
    dice: DiceProvider,
) -> tuple[BattleEvent | None, int]:
    state = combatant.state
    if state.template.kind != "character" or state.current_hp != 0:
        return None, sequence
    if state.is_dead or state.is_stable:
        return None, sequence
    event = resolve_death_save(sequence, round_number, combatant.combatant_id, state, dice)
    return event, sequence + 1


def _end_turn_lifecycle(sequence, round_number, member, setup, dice):
    events, sequence = end_invalid_presence(sequence, round_number, member, setup)
    lifecycle, sequence = resolve_target_condition_timing(
        sequence, round_number, member, "target_turn_end", dice,
    )
    events.extend(lifecycle)
    exile_events, sequence = resolve_source_exile_returns(
        sequence, round_number, member, setup, dice,
    )
    events.extend(exile_events)
    source_events, sequence = resolve_source_condition_timing(
        sequence, round_number, member, setup, "source_turn_end",
    )
    events.extend(source_events)
    delayed, sequence = resolve_delayed_resource_refill_end_turn(
        sequence, round_number, member,
    )
    events.extend(delayed)
    zone_events, sequence = resolve_save_zone_window(
        sequence, round_number, member, setup, dice,
        f"{round_number}:{member.combatant_id}", "end_turn",
    )
    events.extend(zone_events)
    expire_source_turn_modifiers(
        [entry.state for entry in [*setup.heroes, *setup.monsters]],
        member.combatant_id,
        round_number,
    )
    from app.combat.temporary_terrain import expire_source_terrain
    expire_source_terrain(setup, member.combatant_id, round_number)
    expire_current_turn_type_resistances(setup)
    return events, sequence


def run_encounter(selection: EncounterSelection, dice: DiceProvider) -> EncounterBattleResult:
    """Run the currently certified combat subset over a 1-6 vs. 1-6 encounter."""
    try:
        setup = build_encounter_setup(selection)
        events, sequence = prepare_opening_buffs(setup, 1)
        initiative = roll_encounter_initiative(setup, dice)
        combatants = [*setup.heroes, *setup.monsters]
        by_id = _combatant_index(combatants)
        affected_states = [member.state for member in combatants]
        initiative_events, sequence = build_initiative_events(initiative, sequence)
        events.extend(initiative_events)
        refill_events, sequence = resolve_initiative_resource_refills(sequence, setup, dice)
        events.extend(refill_events)

        for round_number in range(1, MAX_ENCOUNTER_ROUNDS + 1):
            for member in combatants:
                member.state.current_round = round_number
            round_turn_order = initiative.first_round_turn_order if round_number == 1 else initiative.turn_order
            for combatant_id in round_turn_order:
                outcome = resolve_encounter_outcome(setup)
                if outcome != "active":
                    events.append(build_finish_event(sequence, round_number, outcome))
                    return build_encounter_result(setup, initiative, events, outcome, round_number)

                member = by_id[combatant_id]
                cleanup_disabled_source_effects(setup)
                expire_source_turn_start_modifiers(affected_states, member.combatant_id)
                refresh_start_of_turn(member.state)
                end_concentration_if_expired(member.state, round_number, affected_states)
                cleanup_persistent_barriers(setup, round_number)
                expiry_events, sequence = expire_start_of_turn_conditions(
                    sequence, round_number, member, setup,
                )
                events.extend(expiry_events)
                save_dot_events, sequence = resolve_start_of_turn_save_condition_damage_events(
                    sequence, round_number, member, setup, dice,
                )
                events.extend(save_dot_events)
                lifecycle_events, sequence = resolve_target_condition_timing(
                    sequence, round_number, member, "target_turn_start", dice,
                )
                events.extend(lifecycle_events)
                expire_suppression_zones(setup, round_number)
                sync_suppression_zone_effects(setup, round_number)
                emanation_events, sequence = resolve_target_turn_start_emanations(
                    sequence, round_number, member, setup, dice,
                    turn_key=f"{round_number}:{member.combatant_id}",
                )
                events.extend(emanation_events)
                zone_events, sequence = resolve_save_zone_window(
                    sequence, round_number, member, setup, dice,
                    f"{round_number}:{member.combatant_id}", "start_turn",
                )
                events.extend(zone_events)
                start_buff = resolve_start_turn_timed_self_buff(
                    sequence, round_number, member, setup,
                )
                if start_buff is not None:
                    events.append(start_buff)
                    sequence += 1

                death_event, sequence = _resolve_zero_hp_turn(sequence, round_number, member, dice)
                if death_event is not None:
                    events.append(death_event)
                if member.state.current_hp <= 0 or member.state.is_dead:
                    end_events, sequence = _end_turn_lifecycle(sequence, round_number, member, setup, dice)
                    events.extend(end_events)
                    continue

                target = select_nearest_target(member, setup)
                if target is not None:
                    turn_events, sequence = resolve_combat_turn(
                        sequence, round_number, member, target, setup, dice,
                    )
                    events.extend(turn_events)
                end_events, sequence = _end_turn_lifecycle(sequence, round_number, member, setup, dice)
                events.extend(end_events)

            outcome = resolve_encounter_outcome(setup)
            if outcome != "active":
                events.append(build_finish_event(sequence, round_number, outcome))
                return build_encounter_result(setup, initiative, events, outcome, round_number)

        events.append(build_finish_event(sequence, MAX_ENCOUNTER_ROUNDS, "draw"))
        return build_encounter_result(setup, initiative, events, "draw", MAX_ENCOUNTER_ROUNDS)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Encounter execution failed.")
        raise RuntimeError("Encounter execution failed.") from exc
