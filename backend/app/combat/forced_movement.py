from __future__ import annotations

from math import gcd

from app.combat.grid_geometry import position_in_bounds
from app.combat.grid_pathing_support import overlapping_occupants
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _ray_step(source: GridPosition, mover: GridPosition) -> tuple[int, int]:
    """Return the smallest integer grid vector that preserves the source-to-mover ray."""
    dx = mover.x - source.x
    dy = mover.y - source.y
    divisor = gcd(abs(dx), abs(dy))
    if divisor == 0:
        return 0, 0
    return dx // divisor, dy // divisor


def push_straight_away(
    mover: EncounterCombatant,
    source: EncounterCombatant,
    setup: EncounterSetup,
    distance_ft: int,
) -> int:
    """Move directly away on the exact grid ray without spending Speed or provoking OAs."""
    if distance_ft < 0 or distance_ft % 5:
        raise ValueError("Forced movement distance must be a nonnegative multiple of 5 feet.")
    if setup.map_definition is None or mover.state.position is None or source.state.position is None:
        raise ValueError("Forced grid movement requires authoritative positions.")
    step_x, step_y = _ray_step(source.state.position, mover.state.position)
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
