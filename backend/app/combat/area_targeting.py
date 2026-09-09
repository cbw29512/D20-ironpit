from __future__ import annotations

from math import hypot

from app.domain.actions import SavingThrowAction
from app.domain.areas import AreaTargeting
from app.domain.encounters import EncounterCombatant, EncounterSetup

CELL_FT = 5


def _living(member: EncounterCombatant) -> bool:
    state = member.state
    return state.is_alive and not state.is_dead and state.current_hp > 0


def _members(actor: EncounterCombatant, setup: EncounterSetup) -> tuple[list[EncounterCombatant], list[EncounterCombatant]]:
    return (setup.monsters, setup.heroes) if actor.side == "heroes" else (setup.heroes, setup.monsters)


def _coord(member: EncounterCombatant, rows: list[EncounterCombatant]) -> tuple[float, float]:
    return float(rows.index(member) * CELL_FT), float(member.position_ft)


def _source_coord(actor: EncounterCombatant, setup: EncounterSetup) -> tuple[float, float]:
    own = setup.heroes if actor.side == "heroes" else setup.monsters
    return _coord(actor, own)


def _directed_inside(area: AreaTargeting, source: tuple[float, float], point: tuple[float, float], aim: tuple[float, float]) -> bool:
    dx, dy = aim[0] - source[0], aim[1] - source[1]
    magnitude = hypot(dx, dy)
    if magnitude == 0:
        return False
    ux, uy = dx / magnitude, dy / magnitude
    px, py = point[0] - source[0], point[1] - source[1]
    forward = px * ux + py * uy
    if forward < 0 or area.length_ft is None or forward > area.length_ft:
        return False
    perpendicular = abs(px * uy - py * ux)
    if area.shape == "line":
        return perpendicular <= (area.width_ft or CELL_FT) / 2
    return perpendicular <= forward / 2


def _point_area_inside(area: AreaTargeting, center: tuple[float, float], point: tuple[float, float]) -> bool:
    return hypot(point[0] - center[0], point[1] - center[1]) <= (area.radius_ft or 0)


def _best_directed(actor, setup, enemies, area) -> tuple[str, ...]:
    source = _source_coord(actor, setup)
    enemy_rows, _ = _members(actor, setup)
    candidates: list[tuple[str, ...]] = []
    for aimed in enemies:
        aim = _coord(aimed, enemy_rows)
        ids = tuple(
            member.combatant_id for member in enemies
            if _directed_inside(area, source, _coord(member, enemy_rows), aim)
        )
        if ids:
            candidates.append(ids)
    return max(candidates, key=lambda ids: (len(ids), ids), default=())


def _best_point_area(actor, setup, enemies, area) -> tuple[str, ...]:
    source = _source_coord(actor, setup)
    enemy_rows, _ = _members(actor, setup)
    centers = [_coord(member, enemy_rows) for member in enemies]
    legal_centers = [center for center in centers if hypot(center[0] - source[0], center[1] - source[1]) <= area.origin_range_ft]
    candidates = [
        tuple(member.combatant_id for member in enemies if _point_area_inside(area, center, _coord(member, enemy_rows)))
        for center in legal_centers
    ]
    return max(candidates, key=lambda ids: (len(ids), ids), default=())


def area_target_ids(actor: EncounterCombatant, setup: EncounterSetup, action: SavingThrowAction) -> tuple[str, ...]:
    """Return opposing targets covered by the best legal placement of the printed area."""
    area = action.area
    if area is None:
        return ()
    enemies, _ = _members(actor, setup)
    living = [member for member in enemies if _living(member)]
    if not living:
        return ()
    if area.shape in {"cone", "line"}:
        return _best_directed(actor, setup, living, area)
    if area.shape == "emanation":
        source = _source_coord(actor, setup)
        enemy_rows, _ = _members(actor, setup)
        return tuple(
            member.combatant_id for member in living
            if _point_area_inside(area, source, _coord(member, enemy_rows))
        )
    return _best_point_area(actor, setup, living, area)
