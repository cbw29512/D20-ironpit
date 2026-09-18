from __future__ import annotations

from app.combat.grid_geometry import position_in_bounds
from app.combat.grid_pathing_support import overlapping_occupants
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def push_straight_away(
    mover: EncounterCombatant,
    source: EncounterCombatant,
    setup: EncounterSetup,
    distance_ft: int,
) -> int:
    """Move a target directly away from a source without spending Speed or provoking OAs."""
    if distance_ft < 0 or distance_ft % 5:
        raise ValueError("Forced movement distance must be a nonnegative multiple of 5 feet.")
    if setup.map_definition is None or mover.state.position is None or source.state.position is None:
        raise ValueError("Forced grid movement requires authoritative positions.")
    dx = mover.state.position.x - source.state.position.x
    dy = mover.state.position.y - source.state.position.y
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
    if step_x == 0 and step_y == 0:
        return 0
    members = [*setup.heroes, *setup.monsters]
    moved = 0
    for _ in range(distance_ft // 5):
        destination = GridPosition(
            x=mover.state.position.x + step_x,
            y=mover.state.position.y + step_y,
        )
        if not position_in_bounds(setup.map_definition, destination, mover.state.template.size):
            break
        if overlapping_occupants(mover, destination, members):
            break
        mover.state.position = destination
        moved += 5
    return moved
