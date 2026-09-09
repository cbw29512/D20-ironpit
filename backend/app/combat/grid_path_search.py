from __future__ import annotations

import heapq
import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.combat.grid_path_search import search_path_toward
from app.combat.grid_pathing_support import movement_step_cost_ft, overlapping_occupants, position_for, reconstruct_path
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, GridPosition

logger = logging.getLogger(__name__)

# A* route-search behavior is adapted from BattleCast ai-movement.ts at
# ffe036c758f18e772a808f538fe3baa845b9bcc0 (MIT, Bartosz Jedrzejewski).
# See docs/BATTLECAST_MOVEMENT_PROVENANCE.md for the full notice.
_NEIGHBOR_OFFSETS = (
    (0, -1), (-1, 0), (1, 0), (0, 1),
    (-1, -1), (1, -1), (-1, 1), (1, 1),
)


def _diagonal_step_allowed(
    map_definition: BattleMapDefinition,
    mover: EncounterCombatant,
    current: GridPosition,
    destination: GridPosition,
    members: list[EncounterCombatant],
) -> bool:
    """Reject diagonal squeezing only when both orthogonal side steps are blocked."""
    try:
        dx = destination.x - current.x
        dy = destination.y - current.y
        if dx == 0 or dy == 0:
            return True
        side_x = GridPosition(x=current.x + dx, y=current.y)
        side_y = GridPosition(x=current.x, y=current.y + dy)
        return (
            movement_step_cost_ft(map_definition, mover, side_x, members) is not None
            or movement_step_cost_ft(map_definition, mover, side_y, members) is not None
        )
    except Exception:
        logger.exception("Failed to validate diagonal movement for %s.", mover.combatant_id)
        raise


def search_path_toward(
    map_definition: BattleMapDefinition,
    mover: EncounterCombatant,
    target: EncounterCombatant,
    members: list[EncounterCombatant],
    desired_distance_ft: int,
) -> list[GridPosition]:
    """Search the full legal map for a direct, deterministic route toward the target."""
    try:
        if desired_distance_ft < 0:
            raise ValueError("Desired distance cannot be negative.")
        start = position_for(mover)
        target_position = position_for(target)
        start_key = (start.x, start.y)
        costs: dict[tuple[int, int], int] = {start_key: 0}
        previous: dict[tuple[int, int], tuple[int, int]] = {}
        start_distance = footprint_distance_ft(
            start, mover.state.template.size, target_position, target.state.template.size,
        )
        start_alignment = abs(start.x - target_position.x) + abs(start.y - target_position.y)
        queue: list[tuple[int, int, int, int, int]] = [
            (max(0, start_distance - desired_distance_ft), start_alignment, 0, start.x, start.y),
        ]
        best = start_key
        best_score = (max(0, start_distance - desired_distance_ft), start_distance, 0, start.x, start.y)

        while queue:
            _, _, cost, x, y = heapq.heappop(queue)
            key = (x, y)
            if cost != costs.get(key):
                continue
            current = GridPosition(x=x, y=y)
            distance = footprint_distance_ft(
                current, mover.state.template.size, target_position, target.state.template.size,
            )
            final_legal = not overlapping_occupants(mover, current, members)
            score = (max(0, distance - desired_distance_ft), distance, cost, x, y)
            if final_legal and score < best_score:
                best, best_score = key, score
            if final_legal and distance <= desired_distance_ft:
                return reconstruct_path(key, previous)

            for dx, dy in _NEIGHBOR_OFFSETS:
                next_x, next_y = x + dx, y + dy
                if next_x < 0 or next_y < 0:
                    continue
                destination = GridPosition(x=next_x, y=next_y)
                step_cost = movement_step_cost_ft(map_definition, mover, destination, members)
                if step_cost is None or not _diagonal_step_allowed(
                    map_definition, mover, current, destination, members,
                ):
                    continue
                next_cost = cost + step_cost
                next_key = (next_x, next_y)
                if next_cost >= costs.get(next_key, 10**9):
                    continue
                costs[next_key] = next_cost
                previous[next_key] = key
                next_distance = footprint_distance_ft(
                    destination, mover.state.template.size, target_position, target.state.template.size,
                )
                heuristic = max(0, next_distance - desired_distance_ft)
                alignment = abs(next_x - target_position.x) + abs(next_y - target_position.y)
                heapq.heappush(queue, (next_cost + heuristic, alignment, next_cost, next_x, next_y))

        return reconstruct_path(best, previous)
    except Exception:
        logger.exception("Full-map path search failed for %s toward %s.", mover.combatant_id, target.combatant_id)
        raise
