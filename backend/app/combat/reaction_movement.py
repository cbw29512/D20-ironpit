from __future__ import annotations

from app.combat.dice import DiceProvider
from app.combat.encounter_movement import move_toward_combatant
from app.combat.grapple import speed_is_zero
from app.combat.opportunity_attacks import MovementSource, resolve_opportunity_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


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
) -> tuple[list[BattleEvent], int, BattleEvent | None]:
    """Open departure Reaction windows, then apply the intended move if it can continue."""
    proposed_position, moved = _proposed_position(mover, target, desired_distance_ft)
    if moved <= 0:
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
                movement_source, dice, disengaged=disengaged,
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
