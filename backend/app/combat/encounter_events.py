from __future__ import annotations

import logging
import uuid

from app.domain.encounters import EncounterBattleResult, EncounterInitiative, EncounterSetup, InitiativeGroup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _same_initiative_bucket(left: InitiativeGroup, right: InitiativeGroup) -> bool:
    try:
        return (left.natural_roll == 1) == (right.natural_roll == 1)
    except Exception as exc:
        logger.exception("Failed to compare initiative priority buckets.")
        raise RuntimeError("Initiative priority buckets could not be compared.") from exc


def _initiative_tie_note(group: InitiativeGroup, groups: list[InitiativeGroup]) -> str:
    try:
        tied = [
            other for other in groups
            if other.initiative_count == group.initiative_count
            and _same_initiative_bucket(group, other)
        ]
        if len(tied) < 2:
            return ""
        sides = {other.side for other in tied}
        if sides == {"heroes"}:
            return " Tied initiative: players decide; party order."
        if sides == {"monsters"}:
            return " Tied initiative: DM decides; encounter order."
        return " Tied initiative: DM decides; heroes act before monsters, then encounter order."
    except Exception as exc:
        logger.exception("Failed to describe initiative tie ownership.")
        raise RuntimeError("Initiative tie note could not be resolved.") from exc


def build_initiative_events(
    initiative: EncounterInitiative,
    sequence: int,
) -> tuple[list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        for group in initiative.groups:
            description = f"{', '.join(group.combatant_ids)} act at Initiative {group.initiative_count}."
            if group.natural_roll == 1:
                description += " Natural 1: bottom initiative priority."
            description += _initiative_tie_note(group, initiative.groups)
            events.append(BattleEvent(
                sequence=sequence,
                round_number=0,
                event_type="initiative",
                actor_id=group.combatant_ids[0],
                actor_name=group.template_id,
                attack_roll=group.initiative_roll,
                animation="initiative",
                description=description,
            ))
            sequence += 1
        for extra in initiative.first_round_extra_turns:
            actor_name = next(
                (
                    event.actor_name for event in events
                    if event.event_type == "initiative" and event.actor_id == extra.combatant_id
                ),
                extra.combatant_id,
            )
            events.append(BattleEvent(
                sequence=sequence,
                round_number=0,
                event_type="feature",
                actor_id=extra.combatant_id,
                actor_name=actor_name,
                feature_id=extra.source_id,
                animation="initiative",
                description=(
                    f"{actor_name} gains an extra first-round turn "
                    f"at Initiative {extra.initiative_count} from {extra.source_name}."
                ),
            ))
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Failed to build initiative and extra-turn audit events.")
        raise RuntimeError("Initiative audit events could not be built.") from exc


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
        ruleset=setup.ruleset,
    )
