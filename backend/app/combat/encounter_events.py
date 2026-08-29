from __future__ import annotations

import uuid

from app.domain.encounters import EncounterBattleResult, EncounterInitiative, EncounterSetup
from app.domain.models import BattleEvent, DiceRoll


def build_initiative_events(
    initiative: EncounterInitiative,
    sequence: int,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    for group in initiative.groups:
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
            description=f"{', '.join(group.combatant_ids)} act at Initiative {group.initiative_count}.",
        ))
        sequence += 1
    return events, sequence


def build_finish_event(sequence: int, round_number: int, outcome: str) -> BattleEvent:
    if outcome == "draw":
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="draw",
            actor_id="arena",
            actor_name="Iron Pit",
            animation="draw",
            description="The encounter ends without a winning side.",
        )
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


def build_encounter_result(
    setup: EncounterSetup,
    initiative: EncounterInitiative,
    events: list[BattleEvent],
    outcome: str,
    rounds: int,
) -> EncounterBattleResult:
    return EncounterBattleResult(
        battle_id=str(uuid.uuid4()),
        outcome=outcome,
        rounds=rounds,
        setup=setup,
        initiative=initiative,
        events=events,
    )
