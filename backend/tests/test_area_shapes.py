from __future__ import annotations

from app.combat.area_shapes import cone_contains, line_contains, radius_contains
from app.domain.targeting import AreaTargeting


def test_area_schema_fails_closed_on_invalid_shape_dimensions() -> None:
    AreaTargeting(shape="radius", origin="point", radius_ft=20)
    AreaTargeting(shape="cone", origin="self", length_ft=30)
    AreaTargeting(shape="line", origin="self", length_ft=60, width_ft=5)
    AreaTargeting(shape="emanation", origin="self", radius_ft=10)
    for kwargs in (
        {"shape": "radius", "origin": "self", "radius_ft": 20},
        {"shape": "cone", "origin": "self", "length_ft": 22},
        {"shape": "line", "origin": "self", "length_ft": 60},
    ):
        try:
            AreaTargeting(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Invalid area targeting was accepted: {kwargs}")


def test_radius_boundary_is_inclusive_and_outside_is_not() -> None:
    assert radius_contains((0.0, 0.0), (15.0, 20.0), 25)
    assert not radius_contains((0.0, 0.0), (15.0, 20.01), 25)


def test_five_foot_line_has_real_width_and_hard_end() -> None:
    direction = (1.0, 0.0)
    assert line_contains((0.0, 0.0), direction, (30.0, 2.5), 30, 5)
    assert not line_contains((0.0, 0.0), direction, (30.0, 2.51), 30, 5)
    assert not line_contains((0.0, 0.0), direction, (30.01, 0.0), 30, 5)


def test_cone_expands_with_distance_and_stops_at_length() -> None:
    direction = (1.0, 0.0)
    assert cone_contains((0.0, 0.0), direction, (10.0, 5.0), 15)
    assert not cone_contains((0.0, 0.0), direction, (10.0, 5.01), 15)
    assert not cone_contains((0.0, 0.0), direction, (15.01, 0.0), 15)
    assert not cone_contains((0.0, 0.0), direction, (-1.0, 0.0), 15)
