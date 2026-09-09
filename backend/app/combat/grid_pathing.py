from __future__ import annotations

import heapq
import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.combat.grid_pathing_support import (
    movement_step_cost_ft,
    overlapping_occupants,
    position_for,
    reconstruct_path,
)
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, GridMovementPlan, GridPosition

logger = logging.getLogger(__name__)
_NEIGHBOR_OFFSETS = tuple(
    (dx, dy)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    if dx or dy
)


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
        start = position_for(mover)
        target_position = position_for(target)
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
            final_legal = not overlapping_occupants(mover, current, members)
            distance = footprint_distance_ft(
                current,
                mover.state.template.size,
                target_position,
                target.state.template.size,
            )
            score = (distance, cost, x, y)
            if final_legal and score < best_score:
                best, best_score = key, score
            if final_legal and distance <= desired_distance_ft:
                return GridMovementPlan(
                    path=reconstruct_path(key, previous),
                    movement_cost_ft=cost,
                    final_distance_ft=distance,
                )

            for dx, dy in _NEIGHBOR_OFFSETS:
                next_x, next_y = x + dx, y + dy
                if next_x < 0 or next_y < 0:
                    continue
                destination = GridPosition(x=next_x, y=next_y)
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
            path=reconstruct_path(best, previous),
            movement_cost_ft=costs[best],
            final_distance_ft=best_score[0],
        )
    except Exception:
        logger.exception(
            "Failed to plan grid movement for %s toward %s.",
            mover.combatant_id,
            target.combatant_id,
        )
        raise
