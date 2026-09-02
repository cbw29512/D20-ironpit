from __future__ import annotations

from app.combat.dice import DiceProvider
from app.combat.encounter_movement import move_toward_combatant
from app.combat.grapple import speed_is_zero
from app.combat.opportunity_attacks import MovementSource, resolve_opportunity_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

FRIGHTENED_EFFECT_ID = "frightened"


def _proposed_position(
    mover: EncounterCombatant,
    target: EncounterCombatant,
    desired_distance_ft: int,
) -> tuple[int, int]:
    if desired_distance_ft < 0:
        raise ValueError("Desired distance cannot be negative.")
    before = abs(mover.position_ft - target.position_ft)
    moved = min(max(0, before - desired_distance_ft), mover.state.movement_remaining_ft)
    direction = 1 if mover.position_ft < target.position_ft else -1
    return mover.position_ft + direction * moved, moved


def _fear_source_ids(mover: EncounterCombatant) -> set[str]:
    if FRIGHTENED_EFFECT_ID not in mover.state.active_effect_ids:
        return set()
    return {
        effect.source_id for effect in mover.state.timed_effects
        if effect.effect_id == FRIGHTENED_EFFECT_ID
    }


def _approaches_fear_source(
    mover: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup | None,
    proposed_position: int,
) -> bool:
    source_ids = _fear_source_ids(mover)
    if not source_ids:
        return False
    if setup is None:
        return (
            target.combatant_id in source_ids
            and abs(proposed_position - target.position_ft) < abs(mover.position_ft - target.position_ft)
        )
    members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
    for source_id in source_ids:
        source = members.get(source_id)
        if source is None:
            continue
        before = abs(mover.position_ft - source.position_ft)
        after = abs(proposed_position - source.position_ft)
        if after < before:
            return True
    return False


def move_toward_with_reactions(
    sequence: int,
    round_number: int,
    mover: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup | None,
    desired_distance_ft: int,
    dice: DiceProvider,
    *,
    movement_source: MovementSource = "speed",
    disengaged: bool = False,
    turn_key: str | None = None,
) -> tuple[list[BattleEvent], int, BattleEvent | None]:
    """Open departure Reaction windows, then apply the intended move if it can continue."""
    proposed_position, moved = _proposed_position(mover, target, desired_distance_ft)
    if moved <= 0 or _approaches_fear_source(mover, target, setup, proposed_position):
        return [], sequence, None

    events: list[BattleEvent] = []
    was_prone = "prone" in mover.state.active_effect_ids
    if setup is not None:
        reactors = setup.monsters if mover.side == "heroes" else setup.heroes
        for reactor in reactors:
            before = abs(reactor.position_ft - mover.position_ft)
            after = abs(reactor.position_ft - proposed_position)
            event = resolve_opportunity_attack(
                sequence, round_number, reactor, mover, setup, before, after,
                movement_source, dice, disengaged=disengaged, turn_key=turn_key,
            )
            if event is None:
                continue
            events.append(event)
            sequence += 1
            newly_prone = not was_prone and "prone" in mover.state.active_effect_ids
            if mover.state.is_dead or mover.state.is_unconscious or speed_is_zero(mover.state) or newly_prone:
                return events, sequence, None

    movement = move_toward_combatant(
        sequence, round_number, mover, target, desired_distance_ft,
    )
    if movement is not None:
        events.append(movement)
        sequence += 1
    return events, sequence, movement
