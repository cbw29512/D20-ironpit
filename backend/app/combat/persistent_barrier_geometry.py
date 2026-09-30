from __future__ import annotations

import logging
from collections import deque

from app.combat.grid_geometry import footprint_distance_ft, occupied_cells
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_barriers import GridBarrierEdge, PersistentBarrierAction
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

Vertex = tuple[int, int]


def edge_vertices(edge: GridBarrierEdge) -> tuple[Vertex, Vertex]:
    """Return physical grid-line vertices for one blocked cell transition."""
    try:
        a, b = edge.first, edge.second
        if a.y == b.y:
            boundary_x = max(a.x, b.x)
            return (boundary_x, a.y), (boundary_x, a.y + 1)
        boundary_y = max(a.y, b.y)
        return (a.x, boundary_y), (a.x + 1, boundary_y)
    except Exception as exc:
        logger.exception("Failed to derive barrier edge vertices.")
        raise RuntimeError("Barrier edge geometry could not be resolved.") from exc


def _section_is_straight_connected(edges: list[GridBarrierEdge]) -> bool:
    try:
        segments = [edge_vertices(edge) for edge in edges]
        horizontal = [first[1] == second[1] for first, second in segments]
        if len(set(horizontal)) != 1:
            return False
        if horizontal[0]:
            if len({first[1] for first, _ in segments}) != 1:
                return False
        elif len({first[0] for first, _ in segments}) != 1:
            return False
        vertices = {vertex for segment in segments for vertex in segment}
        adjacency: dict[Vertex, set[Vertex]] = {vertex: set() for vertex in vertices}
        for first, second in segments:
            adjacency[first].add(second)
            adjacency[second].add(first)
        return len(vertices) == len(edges) + 1 and sum(len(items) == 1 for items in adjacency.values()) == 2
    except Exception:
        logger.exception("Failed to validate barrier section geometry.")
        raise


def _all_segments_connected(section_edges: list[list[GridBarrierEdge]]) -> bool:
    try:
        segments = [edge_vertices(edge) for group in section_edges for edge in group]
        if not segments:
            return False
        adjacency: dict[Vertex, set[Vertex]] = {}
        for first, second in segments:
            adjacency.setdefault(first, set()).add(second)
            adjacency.setdefault(second, set()).add(first)
        seen: set[Vertex] = set()
        queue: deque[Vertex] = deque([segments[0][0]])
        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            queue.extend(adjacency.get(current, ()))
        return seen == set(adjacency)
    except Exception:
        logger.exception("Failed to validate barrier connectivity.")
        raise


def validate_barrier_layout(
    action: PersistentBarrierAction,
    section_edges: list[list[GridBarrierEdge]],
    caster: EncounterCombatant,
    setup: EncounterSetup,
) -> None:
    """Fail closed on illegal section count, geometry, range, bounds, or creature cuts."""
    try:
        if setup.map_definition is None or caster.state.position is None:
            raise ValueError("Persistent barriers require the authoritative grid.")
        if not action.min_sections <= len(section_edges) <= action.max_sections:
            raise ValueError(\n                f"{action.name} requires between {action.min_sections} and "
                f"{action.max_sections} sections."\n            )
        expected_edges = action.section_length_ft // 5
        seen_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
        members = [*setup.heroes, *setup.monsters]

        for group in section_edges:
            if len(group) != expected_edges or not _section_is_straight_connected(group):
                raise ValueError(
                    f"Each {action.name} section must be one straight {action.section_length_ft}-foot panel."
                )
            for edge in group:
                key = edge.canonical_key()
                if key in seen_edges:
                    raise ValueError(f"{action.name} cannot reuse the same barrier edge.")
                seen_edges.add(key)
                for cell in (edge.first, edge.second):
                    if not (
                        0 <= cell.x < setup.map_definition.width_squares
                        and 0 <= cell.y < setup.map_definition.height_squares
                    ):
                        raise ValueError(f"{action.name} barrier edge lies outside the map.")
                distance = min(
                    footprint_distance_ft(
                        caster.state.position,
                        caster.state.template.size,
                        cell,
                        CreatureSize.MEDIUM,
                    )
                    for cell in (edge.first, edge.second)
                )
                if distance > action.cast_range_ft:
                    raise ValueError(f"{action.name} barrier edge exceeds its cast range.")
                for member in members:
                    if member.state.position is None:
                        continue
                    cells = occupied_cells(member.state.position, member.state.template.size)
                    if (edge.first.x, edge.first.y) in cells and (edge.second.x, edge.second.y) in cells:
                        raise ValueError(f"{action.name} placement would cut through a creature space.")

        if action.sections_must_be_contiguous and not _all_segments_connected(section_edges):
            raise ValueError(f"{action.name} sections must form one contiguous barrier.")
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to validate persistent barrier layout for %s.", action.id)
        raise RuntimeError("Persistent barrier layout could not be validated.") from exc
