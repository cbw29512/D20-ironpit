from __future__ import annotations

from app.combat.action_economy import spend
from app.combat.conditions import PRONE_EFFECT_ID
from app.combat.grid_geometry import footprint_distance_ft, position_in_bounds
from app.combat.grid_pathing_support import overlapping_occupants
from app.combat.modifier_stack import effective_speed
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import BattleEvent


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _source(member: EncounterCombatant, setup: EncounterSetup) -> EncounterCombatant | None:
    swallowed = member.state.swallowed
    if swallowed is None:
        return None
    return next((item for item in _members(setup) if item.combatant_id == swallowed.source_id), None)


def _turn_damage(events: list[BattleEvent], attacker_id: str, target_id: str) -> int:
    return sum(
        max(0, event.hp_before - event.hp_after)
        for event in events
        if event.actor_id == attacker_id and event.target_id == target_id
        and event.hp_before is not None and event.hp_after is not None
    )


def _grid_release_position(
    victim: EncounterCombatant, source: EncounterCombatant, setup: EncounterSetup, range_ft: int,
) -> GridPosition:
    arena = setup.map_definition; origin = source.state.position
    if arena is None or origin is None:
        raise ValueError("Grid Swallow release requires map and source position.")
    candidates: list[tuple[int, int, int, GridPosition]] = []
    for y in range(arena.height_squares):
        for x in range(arena.width_squares):
            position = GridPosition(x=x, y=y)
            if not position_in_bounds(arena, position, victim.state.template.size):
                continue
            distance = footprint_distance_ft(
                position, victim.state.template.size, origin, source.state.template.size,
            )
            if distance > range_ft or overlapping_occupants(victim, position, _members(setup)):
                continue
            candidates.append((distance, y, x, position))
    if not candidates:
        raise ValueError(f"No legal Swallow release space exists within {range_ft} feet.")
    return min(candidates, key=lambda item: item[:3])[3]


def _release(victim: EncounterCombatant, source: EncounterCombatant, setup: EncounterSetup, range_ft: int) -> None:
    swallowed = victim.state.swallowed
    if swallowed is None:
        return
    if victim.state.position is not None or source.state.position is not None:
        if victim.state.position is None or source.state.position is None:
            raise ValueError("Swallow release cannot mix scalar and grid position authority.")
        victim.state.position = _grid_release_position(victim, source, setup, range_ft)
    else:
        victim.position_ft = source.position_ft + range_ft
    victim.state.swallowed = None
    if swallowed.exit_prone and PRONE_EFFECT_ID not in victim.state.active_effect_ids:
        victim.state.active_effect_ids.append(PRONE_EFFECT_ID)


def resolve_corpse_escape(
    sequence: int, round_number: int, member: EncounterCombatant, setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    swallowed = member.state.swallowed
    if swallowed is None or not swallowed.source_dead:
        return [], sequence
    source = _source(member, setup)
    if source is None:
        raise ValueError("Swallowed corpse escape requires its source combatant.")
    required = swallowed.exit_movement_ft
    dashed = False
    if member.state.movement_remaining_ft < required and member.state.action_available:
        spend(member.state, "action")
        member.state.movement_remaining_ft += effective_speed(member.state)
        dashed = True
    if member.state.movement_remaining_ft < required:
        return [], sequence
    member.state.movement_remaining_ft -= required
    _release(member, source, setup, 5)
    event = BattleEvent(
        sequence=sequence, round_number=round_number, event_type="movement",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        target_id=source.combatant_id, target_name=source.state.template.name,
        feature_id="swallow-corpse-escape", movement_ft=required, movement_cost_ft=required,
        animation="movement", description=(
            f"{member.state.template.name} {'Dashes and ' if dashed else ''}uses {required} feet of movement "
            f"to escape {source.state.template.name}'s corpse and exits prone."
        ),
    )
    return [event], sequence + 1


def resolve_end_turn_regurgitation(
    sequence: int, round_number: int, member: EncounterCombatant, setup: EncounterSetup,
    turn_events: list[BattleEvent], dice,
) -> tuple[list[BattleEvent], int]:
    swallowed = member.state.swallowed
    if swallowed is None or swallowed.source_dead or swallowed.regurgitation_damage_threshold is None:
        return [], sequence
    values = (
        swallowed.regurgitation_save_ability, swallowed.regurgitation_save_dc,
        swallowed.regurgitation_range_ft,
    )
    if any(value is None for value in values):
        raise ValueError("Active Swallowed state has incomplete regurgitation data.")
    ability, dc, release_range = values
    source = _source(member, setup)
    if source is None or source.state.is_dead or not source.state.is_alive:
        return [], sequence
    damage = _turn_damage(turn_events, member.combatant_id, source.combatant_id)
    if damage < swallowed.regurgitation_damage_threshold:
        return [], sequence
    roll, succeeded = resolve_saving_throw(source.state, ability, dc, dice)
    released: list[str] = []
    if not succeeded:
        for victim in list(_members(setup)):
            state = victim.state.swallowed
            if state is None or state.source_id != source.combatant_id:
                continue
            _release(victim, source, setup, release_range)
            released.append(victim.state.template.name)
    event = BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=source.combatant_id, actor_name=source.state.template.name,
        target_id=member.combatant_id, target_name=member.state.template.name,
        feature_id="swallow-regurgitation", saving_throw_roll=roll,
        save_ability=ability, save_dc=dc, save_succeeded=succeeded,
        animation="forced-movement", description=(
            f"{source.state.template.name} took {damage} damage from inside this turn and "
            f"{'keeps its swallowed creatures' if succeeded else 'regurgitates ' + ', '.join(released)}."
        ),
    )
    return [event], sequence + 1
