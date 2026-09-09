from __future__ import annotations

from app.combat.grid_geometry import (
    footprint_distance_ft,
    footprint_side_squares,
    footprints_overlap,
    occupied_cells,
    position_in_bounds,
)
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.size import CreatureSize


def test_footprint_side_comes_only_from_creature_size() -> None:
    assert footprint_side_squares(CreatureSize.TINY) == 1
    assert footprint_side_squares(CreatureSize.SMALL) == 1
    assert footprint_side_squares(CreatureSize.MEDIUM) == 1
    assert footprint_side_squares(CreatureSize.LARGE) == 2
    assert footprint_side_squares(CreatureSize.HUGE) == 3
    assert footprint_side_squares(CreatureSize.GARGANTUAN) == 4


def test_large_creature_occupies_four_cells() -> None:
    cells = occupied_cells(GridPosition(x=3, y=4), CreatureSize.LARGE)
    assert cells == {(3, 4), (4, 4), (3, 5), (4, 5)}


def test_footprint_bounds_require_entire_creature_on_map() -> None:
    arena = BattleMapDefinition(id="iron-pit-test", width_squares=10, height_squares=10)
    assert position_in_bounds(arena, GridPosition(x=7, y=7), CreatureSize.HUGE)
    assert not position_in_bounds(arena, GridPosition(x=8, y=8), CreatureSize.HUGE)


def test_overlap_is_footprint_aware() -> None:
    assert footprints_overlap(
        GridPosition(x=2, y=2), CreatureSize.LARGE,
        GridPosition(x=3, y=3), CreatureSize.MEDIUM,
    )
    assert not footprints_overlap(
        GridPosition(x=2, y=2), CreatureSize.LARGE,
        GridPosition(x=4, y=4), CreatureSize.MEDIUM,
    )


def test_grid_distance_counts_diagonal_adjacent_cell_as_five_feet() -> None:
    assert footprint_distance_ft(
        GridPosition(x=0, y=0), CreatureSize.MEDIUM,
        GridPosition(x=1, y=1), CreatureSize.MEDIUM,
    ) == 5


def test_grid_distance_uses_nearest_edges_of_large_footprints() -> None:
    assert footprint_distance_ft(
        GridPosition(x=0, y=0), CreatureSize.LARGE,
        GridPosition(x=3, y=0), CreatureSize.LARGE,
    ) == 10
