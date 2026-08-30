from __future__ import annotations

import logging

from app.combat.death_saves import resolve_death_save
from app.combat.dice import DiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_events import (
    build_encounter_result,
    build_finish_event,
    build_initiative_events,
)
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.encounter_outcome import resolve_encounter_outcome
from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import select_nearest_target
from app.combat.state import refresh_reaction
from app.combat.timed_conditions import expire_start_of_turn_conditions
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


def run_encounter(selection: EncounterSelection, dice: DiceProvider) -> EncounterBattleResult:
    """Run the currently certified combat subset over a 1-8 vs. 1-8 encounter."""
    try:
        setup = build_encounter_setup(selection)
        initiative = roll_encounter_initiative(setup, dice)
        by_id = _combatant_index([*setup.heroes, *setup.monsters])
        events, sequence = build_initiative_events(initiative, 1)

        for round_number in range(1, MAX_ENCOUNTER_ROUNDS + 1):
            for combatant_id in initiative.turn_order:
                outcome = resolve_encounter_outcome(setup)
                if outcome != "active":
                    events.append(build_finish_event(sequence, round_number, outcome))
                    return build_encounter_result(
                        setup, initiative, events, outcome, round_number
                    )

                attacker = by_id[combatant_id]
                # RAW refresh happens at the start of every turn. Incapacitation
                # prevents using the Reaction; it does not prevent regaining it.
                refresh_reaction(attacker.state)
                expiry_events, sequence = expire_start_of_turn_conditions(
                    sequence, round_number, attacker, setup
                )
                events.extend(expiry_events)

                death_event, sequence = _resolve_zero_hp_turn(
                    sequence, round_number, attacker, dice
                )
                if death_event is not None:
                    events.append(death_event)
                if attacker.state.current_hp <= 0 or attacker.state.is_dead:
                    continue

                target = select_nearest_target(attacker, setup)
                if target is None:
                    continue
                turn_events, sequence = resolve_combat_turn(
                    sequence, round_number, attacker, target, setup, dice
                )
                events.extend(turn_events)

            outcome = resolve_encounter_outcome(setup)
            if outcome != "active":
                events.append(build_finish_event(sequence, round_number, outcome))
                return build_encounter_result(setup, initiative, events, outcome, round_number)

        events.append(build_finish_event(sequence, MAX_ENCOUNTER_ROUNDS, "draw"))
        return build_encounter_result(
            setup, initiative, events, "draw", MAX_ENCOUNTER_ROUNDS
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Encounter execution failed.")
        raise RuntimeError("Encounter execution failed.") from exc
