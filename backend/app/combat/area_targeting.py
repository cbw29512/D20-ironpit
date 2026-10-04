from __future__ import annotations

import itertools
import logging
from dataclasses import dataclass

from app.combat.barrier_line_of_effect import clear_line_between_points
from app.combat.area_shapes import (
    Direction, Point, cell_center_ft, cone_contains, cube_contains, emanation_contains,
    line_contains, normalized, radius_contains,
)
from app.combat.grid_geometry import occupied_cells
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AreaPlacement:
    target_ids: tuple[str, ...]
    origin: Point
    direction: Direction | None = None
    friendly_ids: tuple[str, ...] = ()
    protected_friendly_ids: tuple[str, ...] = ()
    cube_sw_cells: tuple[tuple[int, int], ...] = ()

    @property
    def enemy_ids(self) -> tuple[str, ...]:
        return self.target_ids


def _points(member: EncounterCombatant, position: GridPosition | None = None) -> tuple[Point, ...]:
    authoritative = position or member.state.position
    if authoritative is None:
        raise ValueError(f"{member.combatant_id} has no authoritative grid position.")
    return tuple(cell_center_ft(x, y) for x, y in occupied_cells(authoritative, member.state.template.size))


def _living_side(actor: EncounterCombatant, setup: EncounterSetup, *, opponents: bool) -> list[EncounterCombatant]:
    if opponents:
        rows = setup.monsters if actor.side == "heroes" else setup.heroes
    else:
        rows = setup.heroes if actor.side == "heroes" else setup.monsters
    return [
        row for row in rows
        if row.combatant_id != actor.combatant_id and row.state.is_alive and not row.state.is_dead and row.state.current_hp > 0
    ]


def _directions(origins: tuple[Point, ...], enemies: list[EncounterCombatant]) -> tuple[Direction, ...]:
    result: set[tuple[float, float]] = set()
    for origin in origins:
        vectors: list[Direction] = []
        for enemy in enemies:
            for point in _points(enemy):
                direction = normalized(point[0] - origin[0], point[1] - origin[1])
                if direction is not None:
                    vectors.append(direction); result.add((round(direction[0], 12), round(direction[1], 12)))
        for first, second in itertools.combinations(vectors, 2):
            direction = normalized(first[0] + second[0], first[1] + second[1])
            if direction is not None: result.add((round(direction[0], 12), round(direction[1], 12)))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        direction = normalized(dx, dy)
        if direction is not None: result.add((round(direction[0], 12), round(direction[1], 12)))
    return tuple(sorted(result))


def _hits(area: AreaTargeting, origins: tuple[Point, ...], origin: Point, direction: Direction | None, target: EncounterCombatant) -> bool:
    points = _points(target)
    if area.shape == "radius": return any(radius_contains(origin, point, area.radius_ft or 0) for point in points)
    if area.shape == "emanation": return any(emanation_contains(origins, point, area.radius_ft or 0) for point in points)
    if direction is None: return False
    if area.shape == "cone": return any(cone_contains(origin, direction, point, area.length_ft or 0) for point in points)
    if area.shape == "cube": return any(cube_contains(origin, direction, point, area.length_ft or 0) for point in points)
    return any(line_contains(origin, direction, point, area.length_ft or 0, area.width_ft or 0) for point in points)


def _point_origins(actor: EncounterCombatant, setup: EncounterSetup, range_ft: int, actor_position: GridPosition | None = None) -> tuple[Point, ...]:
    if setup.map_definition is None: raise ValueError("Area targeting requires an authoritative battle map.")
    actor_points = _points(actor, actor_position); candidates: list[Point] = []
    for x in range(setup.map_definition.width_squares):
        for y in range(setup.map_definition.height_squares):
            point = cell_center_ft(x, y)
            if min(max(abs(point[0] - source[0]), abs(point[1] - source[1])) for source in actor_points) <= range_ft:
                candidates.append(point)
    return tuple(candidates)


def legal_area_placements(actor: EncounterCombatant, setup: EncounterSetup, area: AreaTargeting, range_ft: int, *, actor_position: GridPosition | None = None, allow_no_enemy_targets: bool = False) -> list[AreaPlacement]:
    """Return distinct placements with enemy targets and explicit friendly exposure."""
    try:
        if area.contiguous_section_count:
            from app.combat.contiguous_cube_targeting import legal_contiguous_cube_placements
            return legal_contiguous_cube_placements(
                actor, setup, area, range_ft, actor_position=actor_position,
            )
        enemies = _living_side(actor, setup, opponents=True)
        friends = _living_side(actor, setup, opponents=False)
        if not enemies and not allow_no_enemy_targets: return []
        actor_points = _points(actor, actor_position)
        origins = _point_origins(actor, setup, range_ft, actor_position) if area.origin == "point" else actor_points
        direction_origins = origins if area.origin == "point" else actor_points
        aim_members = enemies if enemies else friends
        directions = (None,) if area.shape in {"radius", "emanation"} else _directions(direction_origins, aim_members)
        placements: dict[tuple[tuple[str, ...], tuple[str, ...], bool], AreaPlacement] = {}
        for origin in origins:
            if (
                area.origin == "point"
                and not clear_line_between_points(actor_points, (origin,), setup.persistent_barriers)
            ):
                continue
            for direction in directions:
                effect_sources = actor_points if area.shape == "emanation" else (origin,)
                target_ids = tuple(
                    enemy.combatant_id
                    for enemy in enemies
                    if _hits(area, actor_points, origin, direction, enemy)
                    and clear_line_between_points(
                        effect_sources,
                        _points(enemy),
                        setup.persistent_barriers,
                    )
                )
                friendly_ids = tuple(
                    friend.combatant_id
                    for friend in friends
                    if _hits(area, actor_points, origin, direction, friend)
                    and clear_line_between_points(
                        effect_sources,
                        _points(friend),
                        setup.persistent_barriers,
                    )
                )
                source_in_area = _hits(area, actor_points, origin, direction, actor)
                if not target_ids and not allow_no_enemy_targets: continue
                if not target_ids and not friendly_ids and not source_in_area: continue
                key = (target_ids, friendly_ids, source_in_area)
                if key not in placements:
                    placements[key] = AreaPlacement(target_ids, origin, direction, friendly_ids)
        return sorted(
            placements.values(),
            key=lambda item: (-len(item.target_ids), len(item.friendly_ids), item.target_ids, item.origin, item.direction or (0.0, 0.0)),
        )
    except Exception:
        logger.exception("Failed universal area targeting for %s.", actor.combatant_id)
        raise


def member_in_area_placement(
    actor: EncounterCombatant,
    member: EncounterCombatant,
    area: AreaTargeting,
    placement: AreaPlacement,
) -> bool:
    """Return whether a combatant occupies any square covered by one resolved area placement."""
    try:
        if placement.cube_sw_cells:
            from app.combat.contiguous_cube_targeting import member_in_contiguous_cubes
            return member_in_contiguous_cubes(member, placement, (area.length_ft or 5) // 5)
        actor_points = _points(actor)
        return _hits(area, actor_points, placement.origin, placement.direction, member)
    except Exception:
        logger.exception(
            "Failed area-membership check for %s in %s's placement.",
            member.combatant_id,
            actor.combatant_id,
        )
        raise
