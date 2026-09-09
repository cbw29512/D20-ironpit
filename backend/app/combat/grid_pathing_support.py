from __future__ import annotations

import logging

from app.combat.grid_geometry import footprints_overlap, position_in_bounds
from app.combat.grid_passage import can_pass_through, creature_space_is_difficult
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, GridPosition

logger = logging.getLogger(__name__)


def position_for(member: EncounterCombatant) -> GridPosition:
    try:
        if member.state.position is None:
            raise ValueError(f"Combatant {member.combatant_id!r} has no authoritative grid position.")
        return member.state.position
    except Exception:
        logger.exception("Failed to read grid position for %s.", member.combatant_id)
        raise


def overlapping_occupants(
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
        for occupant in overlapping_occupants(mover, destination, members):
            if not can_pass_through(mover, occupant):
                return None
            if creature_space_is_difficult(mover, occupant):
                cost = map_definition.cell_size_ft * 2
        return cost
    except Exception:
        logger.exception("Failed to calculate movement step cost for %s.", mover.combatant_id)
        raise


def reconstruct_path(
    end: tuple[int, int],
    previous: dict[tuple[int, int], tuple[int, int]],
) -> list[GridPosition]:
    try:
        path: list[GridPosition] = []
        cursor = end
        while cursor in previous:
            path.append(GridPosition(x=cursor[0], y=cursor[1]))
            cursor = previous[cursor]
        path.reverse()
        return path
    except Exception:
        logger.exception("Failed to reconstruct grid movement path ending at %s.", end)
        raise
