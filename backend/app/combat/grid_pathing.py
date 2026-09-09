from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.combat.grid_path_search import search_path_toward
from app.combat.grid_pathing_support import movement_step_cost_ft, overlapping_occupants, position_for
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, GridMovementPlan, GridPosition

logger = logging.getLogger(__name__)


def _affordable_legal_prefix(
    map_definition: BattleMapDefinition,
    mover: EncounterCombatant,
    members: list[EncounterCombatant],
    route: list[GridPosition],
    movement_budget_ft: int,
) -> tuple[list[GridPosition], int]:
    """Return the farthest legal stopping point along a precomputed full-map route."""
    try:
        spent = 0
        last_legal_index = -1
        last_legal_cost = 0
        for index, destination in enumerate(route):
            step_cost = movement_step_cost_ft(map_definition, mover, destination, members)
            if step_cost is None:
                raise ValueError(f"Search returned an illegal movement step at {destination}.")
            if spent + step_cost > movement_budget_ft:
                break
            spent += step_cost
            if not overlapping_occupants(mover, destination, members):
                last_legal_index = index
                last_legal_cost = spent
        if last_legal_index < 0:
            return [], 0
        return route[: last_legal_index + 1], last_legal_cost
    except Exception:
        logger.exception("Failed to truncate movement route for %s.", mover.combatant_id)
        raise


def plan_movement_toward(
    map_definition: BattleMapDefinition,
    mover: EncounterCombatant,
    target: EncounterCombatant,
    members: list[EncounterCombatant],
    desired_distance_ft: int,
    movement_budget_ft: int,
) -> GridMovementPlan:
    """Search the full route first, then walk the affordable legal prefix this turn."""
    try:
        if desired_distance_ft < 0 or movement_budget_ft < 0:
            raise ValueError("Desired distance and movement budget cannot be negative.")
        route = search_path_toward(
            map_definition,
            mover,
            target,
            members,
            desired_distance_ft,
        )
        target_position = position_for(target)
        route_goal_position = route[-1] if route else position_for(mover)
        route_goal_distance = footprint_distance_ft(
            route_goal_position,
            mover.state.template.size,
            target_position,
            target.state.template.size,
        )
        goal_reachable = route_goal_distance <= desired_distance_ft
        path, cost = _affordable_legal_prefix(
            map_definition,
            mover,
            members,
            route,
            movement_budget_ft,
        )
        final_position = path[-1] if path else position_for(mover)
        final_distance = footprint_distance_ft(
            final_position,
            mover.state.template.size,
            target_position,
            target.state.template.size,
        )
        return GridMovementPlan(
            path=path,
            movement_cost_ft=cost,
            final_distance_ft=final_distance,
            goal_reachable=goal_reachable,
        )
    except Exception:
        logger.exception(
            "Failed to plan grid movement for %s toward %s.",
            mover.combatant_id,
            target.combatant_id,
        )
        raise
