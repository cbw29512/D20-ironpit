from __future__ import annotations

from math import gcd
import logging

from app.combat.grid_barriers import barrier_blocks_transition
from app.combat.grid_geometry import position_in_bounds
from app.combat.grid_pathing_support import overlapping_occupants
from app.combat.persistent_beneficial_zone_effects import sync_persistent_beneficial_zones
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


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
    *,
    round_number: int = 1,
) -> int:
    """Move directly away without spending Speed; stop at creatures, walls, or map edges."""
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
        origin = mover.state.position.model_copy(deep=True)
        destination = GridPosition(
            x=origin.x + step_x,
            y=origin.y + step_y,
        )
        if not position_in_bounds(setup.map_definition, destination, mover.state.template.size):
            break
        if barrier_blocks_transition(origin, destination, setup.persistent_barriers):
            break
        if overlapping_occupants(mover, destination, members):
            break
        mover.state.position = destination
        moved += 5
        sync_persistent_beneficial_zones(setup, round_number)
    return moved


def pull_straight_toward(
    mover: EncounterCombatant,
    source: EncounterCombatant,
    setup: EncounterSetup,
    distance_ft: int,
    *,
    round_number: int = 1,
) -> int:
    """Move directly toward the source without spending Speed; stop before collisions or barriers."""
    try:
        if distance_ft < 0 or distance_ft % 5:
            raise ValueError("Forced movement distance must be a nonnegative multiple of 5 feet.")
        if setup.map_definition is None or mover.state.position is None or source.state.position is None:
            raise ValueError("Forced grid movement requires authoritative positions.")
        away_x, away_y = _ray_step(source.state.position, mover.state.position)
        step_x, step_y = -away_x, -away_y
        if step_x == 0 and step_y == 0:
            return 0
        members = [*setup.heroes, *setup.monsters]
        moved = 0
        for _ in range(distance_ft // 5):
            origin = mover.state.position.model_copy(deep=True)
            destination = GridPosition(x=origin.x + step_x, y=origin.y + step_y)
            if not position_in_bounds(setup.map_definition, destination, mover.state.template.size):
                break
            if barrier_blocks_transition(origin, destination, setup.persistent_barriers):
                break
            if overlapping_occupants(mover, destination, members):
                break
            mover.state.position = destination
            moved += 5
            sync_persistent_beneficial_zones(setup, round_number)
        return moved
    except Exception:
        logger.exception(
            "Forced pull failed for %s toward %s.",
            mover.combatant_id,
            source.combatant_id,
        )
        raise
