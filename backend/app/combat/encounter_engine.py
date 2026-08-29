from __future__ import annotations

import logging
import uuid

from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.encounter_outcome import resolve_encounter_outcome
from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import combatant_distance, select_nearest_target
from app.combat.encounter_turns import prepare_encounter_attack
from app.combat.fighter import use_second_wind
from app.combat.policy import should_use_second_wind
from app.combat.state import begin_turn
from app.domain.encounters import EncounterBattleResult, EncounterCombatant, EncounterSelection
from app.domain.models import BattleEvent, DiceRoll

logger = logging.getLogger(__name__)
MAX_ENCOUNTER_ROUNDS = 100


def _combatant_index(combatants: list[EncounterCombatant]) -> dict[str, EncounterCombatant]:
    return {member.combatant_id: member for member in combatants}


def _initiative_events(result, sequence: int) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    for group in result.groups:
        names = ", ".join(group.combatant_ids)
        roll = DiceRoll(
            notation="1d20",
            rolls=[group.natural_roll],
            modifier=group.initiative_bonus,
            selected_roll=group.natural_roll,
            total=group.initiative_count,
        )
        events.append(BattleEvent(
            sequence=sequence,
            round_number=0,
            event_type="initiative",
            actor_id=group.combatant_ids[0],
            actor_name=group.template_id,
            attack_roll=roll,
            animation="initiative",
            description=f"{names} act at Initiative {group.initiative_count}.",
        ))
        sequence += 1
    return events, sequence


def _victory_event(sequence: int, round_number: int, outcome: str) -> BattleEvent:
    winner = "Heroes" if outcome == "heroes_win" else "Monsters"
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="victory",
        actor_id="arena",
        actor_name="Iron Pit",
        animation="victory",
        description=f"{winner} win. The opposing side is down.",
    )


def run_encounter(selection: EncounterSelection, dice: DiceProvider) -> EncounterBattleResult:
    """Run the currently certified weapon-combat subset over a 1-8 vs. 1-8 encounter."""
    try:
        setup = build_encounter_setup(selection)
        initiative = roll_encounter_initiative(setup, dice)
        all_combatants = [*setup.heroes, *setup.monsters]
        by_id = _combatant_index(all_combatants)
        events, sequence = _initiative_events(initiative, 1)

        for round_number in range(1, MAX_ENCOUNTER_ROUNDS + 1):
            for combatant_id in initiative.turn_order:
                outcome = resolve_encounter_outcome(setup)
                if outcome != "active":
                    events.append(_victory_event(sequence, round_number, outcome))
                    return EncounterBattleResult(
                        battle_id=str(uuid.uuid4()), outcome=outcome, rounds=round_number,
                        setup=setup, initiative=initiative, events=events,
                    )

                attacker = by_id[combatant_id]
                if not attacker.state.is_alive or attacker.state.current_hp <= 0:
                    continue
                target = select_nearest_target(attacker, setup)
                if target is None:
                    continue

                begin_turn(attacker.state)
                if should_use_second_wind(attacker.state):
                    events.append(use_second_wind(
                        sequence, round_number, attacker.state, dice, attacker.combatant_id
                    ))
                    sequence += 1

                attack, prep_events, sequence = prepare_encounter_attack(
                    sequence, round_number, attacker, target
                )
                events.extend(prep_events)
                if attack is None:
                    continue

                events.append(resolve_attack(
                    sequence,
                    round_number,
                    attacker.state,
                    target.state,
                    attack,
                    combatant_distance(attacker, target),
                    dice,
                    actor_event_id=attacker.combatant_id,
                    target_event_id=target.combatant_id,
                ))
                sequence += 1

            outcome = resolve_encounter_outcome(setup)
            if outcome != "active":
                events.append(_victory_event(sequence, round_number, outcome))
                return EncounterBattleResult(
                    battle_id=str(uuid.uuid4()), outcome=outcome, rounds=round_number,
                    setup=setup, initiative=initiative, events=events,
                )

        return EncounterBattleResult(
            battle_id=str(uuid.uuid4()), outcome="active", rounds=MAX_ENCOUNTER_ROUNDS,
            setup=setup, initiative=initiative, events=events,
        )
    except Exception as exc:
        logger.exception("Encounter execution failed.")
        raise RuntimeError("Encounter execution failed.") from exc
