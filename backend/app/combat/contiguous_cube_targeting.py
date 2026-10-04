from __future__ import annotations

import logging

from app.combat.area_shapes import Point, cell_center_ft
from app.combat.area_targeting import AreaPlacement, _living_side, _points
from app.combat.grid_geometry import occupied_cells
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def _span(area: AreaTargeting) -> int:
    length = area.length_ft or 0
    if length < 5 or length % 5:
        raise ValueError("Contiguous cubes require a 5-foot cube length.")
    return length // 5


def _cube_center(sw: tuple[int, int], span: int) -> Point:
    return ((sw[0] + span / 2.0) * 5.0, (sw[1] + span / 2.0) * 5.0)


def _in_range(actor_points: tuple[Point, ...], sw: tuple[int, int], span: int, range_ft: int) -> bool:
    center = _cube_center(sw, span)
    return min(max(abs(center[0] - source[0]), abs(center[1] - source[1])) for source in actor_points) <= range_ft


def _covers(sw: tuple[int, int], span: int, member: EncounterCombatant) -> bool:
    if member.state.position is None:
        return False
    cells = set(occupied_cells(member.state.position, member.state.template.size))
    return any(
        (sw[0] <= x < sw[0] + span and sw[1] <= y < sw[1] + span)
        for x, y in cells
    )


def _adjacent(selected: set[tuple[int, int]], span: int) -> set[tuple[int, int]]:
    found: set[tuple[int, int]] = set()
    for sx, sy in selected:
        for dx, dy in ((span, 0), (-span, 0), (0, span), (0, -span)):
            found.add((sx + dx, sy + dy))
    return found - selected


def _grow(
    seed: tuple[int, int],
    covering: dict[tuple[int, int], set[str]],
    friends: dict[tuple[int, int], set[str]],
    legal: set[tuple[int, int]],
    max_cubes: int,
    span: int,
) -> tuple[tuple[tuple[int, int], ...], set[str], set[str]]:
    selected = {seed}
    covered = set(covering.get(seed, set()))
    exposed = set(friends.get(seed, set()))
    while len(selected) < max_cubes:
        best: tuple[int, int] | None = None
        best_score = (-1, 0)
        for candidate in _adjacent(selected, span):
            if candidate not in legal:
                continue
            gain = len(covering.get(candidate, set()) - covered)
            friend_hit = len(friends.get(candidate, set()) - exposed)
            score = (gain, -friend_hit)
            if score > best_score:
                best, best_score = candidate, score
        if best is None or best_score[0] < 0:
            break
        selected.add(best)
        covered |= covering.get(best, set())
        exposed |= friends.get(best, set())
    return tuple(sorted(selected)), covered, exposed


def legal_contiguous_cube_placements(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    area: AreaTargeting,
    range_ft: int,
    *,
    actor_position: GridPosition | None = None,
) -> list[AreaPlacement]:
    """Place up to N face-adjacent 10-foot cubes to cover the most enemies."""
    try:
        if setup.map_definition is None:
            raise ValueError("Contiguous cube targeting requires an authoritative battle map.")
        span = _span(area)
        max_cubes = area.contiguous_section_count or 1
        actor_points = _points(actor, actor_position)
        enemies = _living_side(actor, setup, opponents=True)
        allies = _living_side(actor, setup, opponents=False)
        width, height = setup.map_definition.width_squares, setup.map_definition.height_squares
        legal: set[tuple[int, int]] = set()
        covering: dict[tuple[int, int], set[str]] = {}
        friends: dict[tuple[int, int], set[str]] = {}
        for sx in range(0, width - span + 1):
            for sy in range(0, height - span + 1):
                sw = (sx, sy)
                if not _in_range(actor_points, sw, span, range_ft):
                    continue
                legal.add(sw)
                hits = {enemy.combatant_id for enemy in enemies if _covers(sw, span, enemy)}
                if hits:
                    covering[sw] = hits
                ally_hits = {ally.combatant_id for ally in allies if _covers(sw, span, ally)}
                if ally_hits:
                    friends[sw] = ally_hits
        if not covering:
            return []
        placements: dict[tuple[tuple[str, ...], tuple[str, ...]], AreaPlacement] = {}
        seeds = sorted(covering, key=lambda item: (-len(covering[item]), item))
        for seed in seeds[:16]:
            cubes, enemy_ids, friend_ids = _grow(seed, covering, friends, legal, max_cubes, span)
            if not enemy_ids:
                continue
            key = (tuple(sorted(enemy_ids)), tuple(sorted(friend_ids)))
            if key in placements:
                continue
            origin = _cube_center(cubes[0], span)
            placements[key] = AreaPlacement(
                tuple(sorted(enemy_ids)),
                origin,
                None,
                tuple(sorted(friend_ids)),
                cube_sw_cells=cubes,
            )
        return sorted(
            placements.values(),
            key=lambda item: (-len(item.target_ids), len(item.friendly_ids), item.target_ids, item.origin),
        )
    except Exception:
        logger.exception("Failed contiguous-cube placement for %s.", actor.combatant_id)
        raise


def member_in_contiguous_cubes(member: EncounterCombatant, placement: AreaPlacement, span: int) -> bool:
    try:
        return any(_covers(sw, span, member) for sw in placement.cube_sw_cells)
    except Exception:
        logger.exception("Failed contiguous-cube membership for %s.", member.combatant_id)
        raise
