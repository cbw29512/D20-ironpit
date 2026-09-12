from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_side_squares, footprints_overlap, position_in_bounds
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


def _sign(value: float) -> int:
    return int(value > 0) - int(value < 0)


def _center(member: EncounterCombatant) -> tuple[float, float]:
    position = member.state.position
    if position is None:
        raise ValueError("Forced movement requires authoritative grid positions.")
    side = footprint_side_squares(member.state.template.size)
    offset = (side - 1) / 2
    return position.x + offset, position.y + offset


def _occupied_by_other(
    target: EncounterCombatant,
    candidate: GridPosition,
    setup: EncounterSetup,
) -> bool:
    for member in [*setup.heroes, *setup.monsters]:
        if member.combatant_id == target.combatant_id or member.state.position is None or member.state.is_dead:
            continue
        if footprints_overlap(
            candidate,
            target.state.template.size,
            member.state.position,
            member.state.template.size,
        ):
            return True
    return False


def push_away(
    source: EncounterCombatant,
    target: EncounterCombatant,
    distance_ft: int,
    setup: EncounterSetup,
) -> int:
    """Push a target straight away on the authoritative grid, stopping at the first illegal cell."""
    try:
        if distance_ft < 0 or distance_ft % 5:
            raise ValueError("Forced push distance must be a nonnegative 5-foot increment.")
        if distance_ft == 0:
            return 0
        if setup.map_definition is None or target.state.position is None:
            raise ValueError("Forced push requires an authoritative battle map and target position.")
        sx, sy = _center(source); tx, ty = _center(target)
        dx, dy = _sign(tx - sx), _sign(ty - sy)
        if dx == 0 and dy == 0:
            raise ValueError("Forced push direction is undefined for overlapping centers.")
        moved = 0
        current = target.state.position.model_copy(deep=True)
        for _ in range(distance_ft // 5):
            candidate = GridPosition(x=current.x + dx, y=current.y + dy)
            if not position_in_bounds(setup.map_definition, candidate, target.state.template.size):
                break
            if _occupied_by_other(target, candidate, setup):
                break
            current = candidate
            moved += 5
        target.state.position = current
        return moved
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Forced push failed for %s -> %s.", source.combatant_id, target.combatant_id)
        raise RuntimeError("Forced movement could not be resolved.") from exc