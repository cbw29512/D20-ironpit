from __future__ import annotations

import itertools
import logging
from dataclasses import dataclass

from app.combat.area_shapes import (
    Direction,
    Point,
    cell_center_ft,
    cone_contains,
    emanation_contains,
    line_contains,
    normalized,
    radius_contains,
)
from app.combat.grid_geometry import occupied_cells
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AreaPlacement:
    target_ids: tuple[str, ...]
    origin: Point
    direction: Direction | None = None


def _points(member: EncounterCombatant) -> tuple[Point, ...]:
    position = member.state.position
    if position is None:
        raise ValueError(f"{member.combatant_id} has no authoritative grid position.")
    return tuple(cell_center_ft(x, y) for x, y in occupied_cells(position, member.state.template.size))


def _living_opponents(actor: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    rows = setup.monsters if actor.side == "heroes" else setup.heroes
    return [row for row in rows if row.state.is_alive and not row.state.is_dead and row.state.current_hp > 0]


def _directions(origins: tuple[Point, ...], enemies: list[EncounterCombatant]) -> tuple[Direction, ...]:
    result: set[tuple[float, float]] = set()
    for origin in origins:
        vectors: list[Direction] = []
        for enemy in enemies:
            for point in _points(enemy):
                direction = normalized(point[0] - origin[0], point[1] - origin[1])
                if direction is not None:
                    vectors.append(direction)
                    result.add((round(direction[0], 12), round(direction[1], 12)))
        for first, second in itertools.combinations(vectors, 2):
            direction = normalized(first[0] + second[0], first[1] + second[1])
            if direction is not None:
                result.add((round(direction[0], 12), round(direction[1], 12)))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        direction = normalized(dx, dy)
        if direction is not None:
            result.add((round(direction[0], 12), round(direction[1], 12)))
    return tuple(sorted(result))


def _hits(area: AreaTargeting, origins: tuple[Point, ...], origin: Point, direction: Direction | None, target: EncounterCombatant) -> bool:
    points = _points(target)
    if area.shape == "radius":
        return any(radius_contains(origin, point, area.radius_ft or 0) for point in points)
    if area.shape == "emanation":
        return any(emanation_contains(origins, point, area.radius_ft or 0) for point in points)
    if direction is None:
        return False
    if area.shape == "cone":
        return any(cone_contains(origin, direction, point, area.length_ft or 0) for point in points)
    return any(line_contains(origin, direction, point, area.length_ft or 0, area.width_ft or 0) for point in points)


def _point_origins(actor: EncounterCombatant, setup: EncounterSetup, range_ft: int) -> tuple[Point, ...]:
    if setup.map_definition is None:
        raise ValueError("Area targeting requires an authoritative battle map.")
    actor_points = _points(actor)
    candidates: list[Point] = []
    for x in range(setup.map_definition.width_squares):
        for y in range(setup.map_definition.height_squares):
            point = cell_center_ft(x, y)
            if min(max(abs(point[0] - source[0]), abs(point[1] - source[1])) for source in actor_points) <= range_ft:
                candidates.append(point)
    return tuple(candidates)


def legal_area_placements(actor: EncounterCombatant, setup: EncounterSetup, area: AreaTargeting, range_ft: int) -> list[AreaPlacement]:
    """Return distinct ally-safe placements against living opponents on the canonical grid."""
    try:
        enemies = _living_opponents(actor, setup)
        if not enemies:
            return []
        actor_points = _points(actor)
        placements: dict[tuple[str, ...], AreaPlacement] = {}
        origins = _point_origins(actor, setup, range_ft) if area.origin == "point" else actor_points
        directions = (None,) if area.shape in {"radius", "emanation"} else _directions(actor_points, enemies)
        for origin in origins:
            for direction in directions:
                target_ids = tuple(enemy.combatant_id for enemy in enemies if _hits(area, actor_points, origin, direction, enemy))
                if target_ids and target_ids not in placements:
                    placements[target_ids] = AreaPlacement(target_ids=target_ids, origin=origin, direction=direction)
        return sorted(placements.values(), key=lambda item: (-len(item.target_ids), item.target_ids, item.origin, item.direction or (0.0, 0.0)))
    except Exception:
        logger.exception("Failed universal area targeting for %s.", actor.combatant_id)
        raise
