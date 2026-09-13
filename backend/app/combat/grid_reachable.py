from __future__ import annotations

import heapq
import logging

from app.combat.grid_pathing_support import movement_step_cost_ft, overlapping_occupants, position_for, reconstruct_path
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, GridDestinationPlan, GridPosition

logger = logging.getLogger(__name__)
_NEIGHBOR_OFFSETS = (
    (0, -1), (-1, 0), (1, 0), (0, 1),
    (-1, -1), (1, -1), (-1, 1), (1, 1),
)


def _diagonal_allowed(
    map_definition: BattleMapDefinition,
    mover: EncounterCombatant,
    current: GridPosition,
    destination: GridPosition,
    members: list[EncounterCombatant],
) -> bool:
    try:
        dx, dy = destination.x - current.x, destination.y - current.y
        if dx == 0 or dy == 0:
            return True
        side_x = GridPosition(x=current.x + dx, y=current.y)
        side_y = GridPosition(x=current.x, y=current.y + dy)
        return (
            movement_step_cost_ft(map_definition, mover, side_x, members) is not None
            or movement_step_cost_ft(map_definition, mover, side_y, members) is not None
        )
    except Exception:
        logger.exception("Failed reachable-grid diagonal check for %s.", mover.combatant_id)
        raise


def reachable_grid_destinations(
    map_definition: BattleMapDefinition,
    mover: EncounterCombatant,
    members: list[EncounterCombatant],
    movement_budget_ft: int,
) -> list[GridDestinationPlan]:
    """Return every legal stopping square reachable within the current movement budget."""
    try:
        if movement_budget_ft < 0:
            raise ValueError("Movement budget cannot be negative.")
        start = position_for(mover)
        start_key = (start.x, start.y)
        costs: dict[tuple[int, int], int] = {start_key: 0}
        previous: dict[tuple[int, int], tuple[int, int]] = {}
        queue: list[tuple[int, int, int]] = [(0, start.x, start.y)]
        plans: list[GridDestinationPlan] = []

        while queue:
            cost, x, y = heapq.heappop(queue)
            key = (x, y)
            if cost != costs.get(key) or cost > movement_budget_ft:
                continue
            current = GridPosition(x=x, y=y)
            if not overlapping_occupants(mover, current, members):
                plans.append(GridDestinationPlan(
                    destination=current,
                    path=reconstruct_path(key, previous),
                    movement_cost_ft=cost,
                ))
            for dx, dy in _NEIGHBOR_OFFSETS:
                destination = GridPosition(x=x + dx, y=y + dy) if x + dx >= 0 and y + dy >= 0 else None
                if destination is None:
                    continue
                step_cost = movement_step_cost_ft(map_definition, mover, destination, members)
                if step_cost is None or not _diagonal_allowed(
                    map_definition, mover, current, destination, members,
                ):
                    continue
                next_cost = cost + step_cost
                next_key = (destination.x, destination.y)
                if next_cost > movement_budget_ft or next_cost >= costs.get(next_key, 10**9):
                    continue
                costs[next_key] = next_cost
                previous[next_key] = key
                heapq.heappush(queue, (next_cost, destination.x, destination.y))
        return sorted(plans, key=lambda plan: (
            plan.movement_cost_ft, plan.destination.x, plan.destination.y,
        ))
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed reachable-grid search for %s.", mover.combatant_id)
        raise RuntimeError("Reachable grid destinations could not be evaluated.") from exc
