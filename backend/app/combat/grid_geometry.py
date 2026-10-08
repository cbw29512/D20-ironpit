from __future__ import annotations

import logging

from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

# Pit magic: creature size does not expand physical square occupation.
_FOOTPRINT_SIDE = {
    CreatureSize.TINY: 1,
    CreatureSize.SMALL: 1,
    CreatureSize.MEDIUM: 1,
    CreatureSize.LARGE: 1,
    CreatureSize.HUGE: 1,
    CreatureSize.GARGANTUAN: 1,
}


def footprint_side_squares(size: CreatureSize) -> int:
    try:
        return _FOOTPRINT_SIDE[size]
    except Exception:
        logger.exception("Failed to derive grid footprint for creature size %r.", size)
        raise


def occupied_cells(position: GridPosition, size: CreatureSize) -> set[tuple[int, int]]:
    try:
        side = footprint_side_squares(size)
        return {
            (position.x + dx, position.y + dy)
            for dx in range(side)
            for dy in range(side)
        }
    except Exception:
        logger.exception("Failed to derive occupied cells at %s for size %s.", position, size)
        raise


def position_in_bounds(
    map_definition: BattleMapDefinition,
    position: GridPosition,
    size: CreatureSize,
) -> bool:
    try:
        side = footprint_side_squares(size)
        return (
            position.x >= 0
            and position.y >= 0
            and position.x + side <= map_definition.width_squares
            and position.y + side <= map_definition.height_squares
        )
    except Exception:
        logger.exception("Failed to validate grid bounds for %s at %s.", size, position)
        raise


def footprints_overlap(
    first_position: GridPosition,
    first_size: CreatureSize,
    second_position: GridPosition,
    second_size: CreatureSize,
) -> bool:
    try:
        return bool(
            occupied_cells(first_position, first_size)
            & occupied_cells(second_position, second_size)
        )
    except Exception:
        logger.exception("Failed to test footprint overlap.")
        raise


def footprint_distance_ft(
    first_position: GridPosition,
    first_size: CreatureSize,
    second_position: GridPosition,
    second_size: CreatureSize,
) -> int:
    """Return shortest 2024-grid distance between occupied footprint cells."""
    try:
        first = occupied_cells(first_position, first_size)
        second = occupied_cells(second_position, second_size)
        if first & second:
            return 0
        cell_steps = min(
            max(abs(ax - bx), abs(ay - by))
            for ax, ay in first
            for bx, by in second
        )
        return cell_steps * 5
    except Exception:
        logger.exception("Failed to calculate footprint-aware grid distance.")
        raise


def square_area_cells(position: GridPosition, side_squares: int) -> set[tuple[int, int]]:
    """Occupied cells for an effect square; independent of creature-size Pit magic."""
    if side_squares < 1:
        raise ValueError("Area square side must be positive.")
    return {
        (position.x + dx, position.y + dy)
        for dx in range(side_squares)
        for dy in range(side_squares)
    }


def square_area_in_bounds(
    map_definition: BattleMapDefinition, position: GridPosition, side_squares: int,
) -> bool:
    if side_squares < 1:
        raise ValueError("Area square side must be positive.")
    return (
        0 <= position.x and 0 <= position.y
        and position.x + side_squares <= map_definition.width_squares
        and position.y + side_squares <= map_definition.height_squares
    )


def square_area_distance_ft(
    first_position: GridPosition, first_side: int,
    second_position: GridPosition, second_side: int,
) -> int:
    first = square_area_cells(first_position, first_side)
    second = square_area_cells(second_position, second_side)
    return min(
        max(abs(ax - bx), abs(ay - by)) * 5
        for ax, ay in first for bx, by in second
    )
