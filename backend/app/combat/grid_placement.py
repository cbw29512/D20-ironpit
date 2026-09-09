from __future__ import annotations

import logging

from app.combat.formation import uses_backline
from app.combat.grid_geometry import footprint_side_squares, footprints_overlap, position_in_bounds
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, DeploymentZone, GridPlacementAssignment, GridPosition

logger = logging.getLogger(__name__)


def _zone_positions(
    map_definition: BattleMapDefinition,
    zone: DeploymentZone,
    member: EncounterCombatant,
) -> list[GridPosition]:
    try:
        side = footprint_side_squares(member.state.template.size)
        max_x = zone.x + zone.width_squares - side
        max_y = zone.y + zone.height_squares - side
        if max_x < zone.x or max_y < zone.y:
            return []
        x_values = list(range(zone.x, max_x + 1))
        backline = uses_backline(member.state.template)
        front_east = zone.front_edge == "east"
        toward_front = not backline
        reverse_x = front_east == toward_front
        x_values.sort(reverse=reverse_x)
        center_y = zone.y + (zone.height_squares - 1) / 2
        y_values = list(range(zone.y, max_y + 1))
        y_values.sort(key=lambda y: (abs((y + (side - 1) / 2) - center_y), y))
        return [
            position
            for x in x_values
            for y in y_values
            if position_in_bounds(
                map_definition,
                position := GridPosition(x=x, y=y),
                member.state.template.size,
            )
        ]
    except Exception:
        logger.exception("Failed to enumerate deployment positions for %s.", member.combatant_id)
        raise


def _overlaps_assignments(
    member: EncounterCombatant,
    position: GridPosition,
    placed: list[tuple[EncounterCombatant, GridPosition]],
) -> bool:
    try:
        return any(
            footprints_overlap(
                position,
                member.state.template.size,
                other_position,
                other.state.template.size,
            )
            for other, other_position in placed
        )
    except Exception:
        logger.exception("Failed to test deployment overlap for %s.", member.combatant_id)
        raise


def _placement_order(members: list[EncounterCombatant]) -> list[EncounterCombatant]:
    try:
        indexed = list(enumerate(members))
        indexed.sort(
            key=lambda item: (
                -footprint_side_squares(item[1].state.template.size),
                uses_backline(item[1].state.template),
                item[0],
            )
        )
        return [member for _, member in indexed]
    except Exception:
        logger.exception("Failed to order combatants for deterministic deployment.")
        raise


def pack_deployment_zone(
    map_definition: BattleMapDefinition,
    zone: DeploymentZone,
    members: list[EncounterCombatant],
) -> list[GridPlacementAssignment]:
    """Pack one side into a legal zone using size-aware deterministic backtracking."""
    try:
        ordered = _placement_order(members)
        placed: list[tuple[EncounterCombatant, GridPosition]] = []

        def search(index: int) -> bool:
            try:
                if index >= len(ordered):
                    return True
                member = ordered[index]
                for position in _zone_positions(map_definition, zone, member):
                    if _overlaps_assignments(member, position, placed):
                        continue
                    placed.append((member, position))
                    if search(index + 1):
                        return True
                    placed.pop()
                return False
            except Exception:
                logger.exception("Deployment search failed at index %s.", index)
                raise

        if not search(0):
            raise ValueError("Combatants cannot fit inside the requested deployment zone.")
        by_id = {member.combatant_id: position for member, position in placed}
        return [
            GridPlacementAssignment(combatant_id=member.combatant_id, position=by_id[member.combatant_id])
            for member in members
        ]
    except Exception:
        logger.exception("Failed to pack %s combatants into deployment zone %s.", len(members), zone)
        raise


def apply_placement(
    members: list[EncounterCombatant],
    assignments: list[GridPlacementAssignment],
) -> None:
    try:
        by_id = {assignment.combatant_id: assignment.position for assignment in assignments}
        if set(by_id) != {member.combatant_id for member in members}:
            raise ValueError("Deployment assignments must match the combatant set exactly.")
        for member in members:
            member.state.position = by_id[member.combatant_id].model_copy(deep=True)
    except Exception:
        logger.exception("Failed to apply authoritative grid placement.")
        raise
