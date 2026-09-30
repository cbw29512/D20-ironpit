from __future__ import annotations

import logging

from app.combat.area_shapes import Point, cell_center_ft
from app.combat.grid_geometry import occupied_cells
from app.combat.persistent_barrier_geometry import edge_vertices
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.persistent_barriers import PersistentBarrierState

logger = logging.getLogger(__name__)


def _orientation(a: Point, b: Point, c: Point) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a: Point, b: Point, c: Point) -> bool:
    return (
        min(a[0], c[0]) <= b[0] <= max(a[0], c[0])
        and min(a[1], c[1]) <= b[1] <= max(a[1], c[1])
    )


def _segments_intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    o1 = _orientation(a, b, c)
    o2 = _orientation(a, b, d)
    o3 = _orientation(c, d, a)
    o4 = _orientation(c, d, b)
    if ((o1 > 0 > o2) or (o1 < 0 < o2)) and ((o3 > 0 > o4) or (o3 < 0 < o4)):
        return True
    if o1 == 0 and _on_segment(a, c, b):
        return True
    if o2 == 0 and _on_segment(a, d, b):
        return True
    if o3 == 0 and _on_segment(c, a, d):
        return True
    if o4 == 0 and _on_segment(c, b, d):
        return True
    return False


def _live_sight_segments(
    barriers: list[PersistentBarrierState] | None,
) -> tuple[tuple[Point, Point], ...]:
    try:
        result: list[tuple[Point, Point]] = []
        for barrier in barriers or []:
            if not barrier.blocks_line_of_sight:
                continue
            for section in barrier.sections:
                if section.destroyed or section.current_hp <= 0:
                    continue
                for edge in section.edges:
                    first, second = edge_vertices(edge)
                    result.append((
                        (first[0] * 5.0, first[1] * 5.0),
                        (second[0] * 5.0, second[1] * 5.0),
                    ))
        return tuple(result)
    except Exception as exc:
        logger.exception("Failed to derive live barrier sight segments.")
        raise RuntimeError("Barrier sight segments could not be resolved.") from exc


def clear_line_between_points(
    sources: tuple[Point, ...],
    targets: tuple[Point, ...],
    barriers: list[PersistentBarrierState] | None,
) -> bool:
    """Return True if at least one source-target ray avoids every live sight-blocking barrier."""
    try:
        segments = _live_sight_segments(barriers)
        if not segments:
            return True
        return any(
            not any(_segments_intersect(source, target, first, second) for first, second in segments)
            for source in sources
            for target in targets
        )
    except Exception as exc:
        logger.exception("Failed to evaluate barrier line of effect.")
        raise RuntimeError("Barrier line of effect could not be evaluated.") from exc


def member_points(member: EncounterCombatant) -> tuple[Point, ...]:
    try:
        if member.state.position is None:
            raise ValueError(f"{member.combatant_id} has no authoritative grid position.")
        return tuple(
            cell_center_ft(x, y)
            for x, y in occupied_cells(member.state.position, member.state.template.size)
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to derive sight points for %s.", member.combatant_id)
        raise RuntimeError("Combatant sight points could not be resolved.") from exc


def clear_line_between_members(
    source: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
) -> bool:
    try:
        if not setup.persistent_barriers:
            return True
        return clear_line_between_points(
            member_points(source),
            member_points(target),
            setup.persistent_barriers,
        )
    except Exception as exc:
        logger.exception(
            "Failed to evaluate line of effect from %s to %s.",
            source.combatant_id,
            target.combatant_id,
        )
        raise RuntimeError("Combatant line of effect could not be evaluated.") from exc
