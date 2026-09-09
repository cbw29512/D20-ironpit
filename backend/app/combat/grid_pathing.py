from __future__ import annotations

import heapq
import logging

from app.combat.grid_geometry import footprint_distance_ft, footprints_overlap, position_in_bounds
from app.combat.grid_passage import can_pass_through, creature_space_is_difficult
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, GridMovementPlan, GridPosition

logger = logging.getLogger(__name__)
_NEIGHBOR_OFFSETS = tuple(
    (dx, dy)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    if dx or dy
)


def _position(member: EncounterCombatant) -> GridPosition:
    try:
        if member.state.position is None:
            raise ValueError(f"Combatant {member.combatant_id!r} has no authoritative grid position.")
        return member.state.position
    except Exception:
        logger.exception("Failed to read grid position for %s.", member.combatant_id)
        raise


def _overlapping_occupants(
    mover: EncounterCombatant,
    destination: GridPosition,
    members: list[EncounterCombatant],
) -> list[EncounterCombatant]:
    try:
        overlaps: list[EncounterCombatant] = []
        for occupant in members:
            if occupant.combatant_id == mover.combatant_id or occupant.state.position is None:
                continue
            if footprints_overlap(
                destination,
                mover.state.template.size,
                occupant.state.position,
                occupant.state.template.size,
            ):
                overlaps.append(occupant)
        return overlaps
    except Exception:
        logger.exception("Failed to resolve occupied destination for %s.", mover.combatant_id)
        raise


def movement_step_cost_ft(
    map_definition: BattleMapDefinition,
    mover: EncounterCombatant,
    destination: GridPosition,
    members: list[EncounterCombatant],
) -> int | None:
    """Return 5/10 feet for a legal adjacent destination, or None when passage is illegal."""
    try:
        if not position_in_bounds(map_definition, destination, mover.state.template.size):
            return None
        cost = map_definition.cell_size_ft
        for occupant in _overlapping_occupants(mover, destination, members):
            if not can_pass_through(mover, occupant):
                return None
            if creature_space_is_difficult(mover, occupant):
                cost = map_definition.cell_size_ft * 2
        return cost
    except Exception:
        logger.exception("Failed to calculate movement step cost for %s.", mover.combatant_id)
        raise


def _reconstruct(
    end: tuple[int, int],
    previous: dict[tuple[int, int], tuple[int, int]],
) -> list[GridPosition]:
    path: list[GridPosition] = []
    cursor = end
    while cursor in previous:
        path.append(GridPosition(x=cursor[0], y=cursor[1]))
        cursor = previous[cursor]
    path.reverse()
    return path


def plan_movement_toward(
    map_definition: BattleMapDefinition,
    mover: EncounterCombatant,
    target: EncounterCombatant,
    members: list[EncounterCombatant],
    desired_distance_ft: int,
    movement_budget_ft: int,
) -> GridMovementPlan:
    """Find the cheapest legal 8-direction grid path toward the requested footprint distance."""
    try:
        if desired_distance_ft < 0 or movement_budget_ft < 0:
            raise ValueError("Desired distance and movement budget cannot be negative.")
        start = _position(mover)
        target_position = _position(target)
        start_key = (start.x, start.y)
        costs = {start_key: 0}
        previous: dict[tuple[int, int], tuple[int, int]] = {}
        queue: list[tuple[int, int, int]] = [(0, start.x, start.y)]
        best = start_key
        best_score = (
            footprint_distance_ft(start, mover.state.template.size, target_position, target.state.template.size),
            0,
            start.x,
            start.y,
        )

        while queue:
            cost, x, y = heapq.heappop(queue)
            key = (x, y)
            if cost != costs.get(key) or cost > movement_budget_ft:
                continue
            current = GridPosition(x=x, y=y)
            occupants = _overlapping_occupants(mover, current, members)
            final_legal = not occupants
            distance = footprint_distance_ft(
                current, mover.state.template.size, target_position, target.state.template.size,
            )
            score = (distance, cost, x, y)
            if final_legal and score < best_score:
                best, best_score = key, score
            if final_legal and distance <= desired_distance_ft:
                return GridMovementPlan(
                    path=_reconstruct(key, previous),
                    movement_cost_ft=cost,
                    final_distance_ft=distance,
                )

            for dx, dy in _NEIGHBOR_OFFSETS:
                destination = GridPosition(x=x + dx, y=y + dy) if x + dx >= 0 and y + dy >= 0 else None
                if destination is None:
                    continue
                step_cost = movement_step_cost_ft(map_definition, mover, destination, members)
                if step_cost is None:
                    continue
                next_cost = cost + step_cost
                next_key = (destination.x, destination.y)
                if next_cost > movement_budget_ft or next_cost >= costs.get(next_key, 10**9):
                    continue
                costs[next_key] = next_cost
                previous[next_key] = key
                heapq.heappush(queue, (next_cost, destination.x, destination.y))

        return GridMovementPlan(
            path=_reconstruct(best, previous),
            movement_cost_ft=costs[best],
            final_distance_ft=best_score[0],
        )
    except Exception:
        logger.exception("Failed to plan grid movement for %s toward %s.", mover.combatant_id, target.combatant_id)
        raise
