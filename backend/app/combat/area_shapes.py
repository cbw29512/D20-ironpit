from __future__ import annotations

import math

Point = tuple[float, float]
Direction = tuple[float, float]
_EPSILON = 1e-9


def cell_center_ft(x: int, y: int) -> Point:
    return ((x + 0.5) * 5.0, (y + 0.5) * 5.0)


def normalized(dx: float, dy: float) -> Direction | None:
    magnitude = math.hypot(dx, dy)
    if magnitude <= _EPSILON:
        return None
    return (dx / magnitude, dy / magnitude)


def radius_contains(origin: Point, point: Point, radius_ft: int) -> bool:
    return math.dist(origin, point) <= radius_ft + _EPSILON


def emanation_contains(origins: tuple[Point, ...], point: Point, radius_ft: int) -> bool:
    return any(radius_contains(origin, point, radius_ft) for origin in origins)


def _projection(origin: Point, direction: Direction, point: Point) -> tuple[float, float]:
    vx, vy = point[0] - origin[0], point[1] - origin[1]
    forward = vx * direction[0] + vy * direction[1]
    sideways = abs(vx * direction[1] - vy * direction[0])
    return forward, sideways


def line_contains(origin: Point, direction: Direction, point: Point, length_ft: int, width_ft: int) -> bool:
    forward, sideways = _projection(origin, direction, point)
    return -_EPSILON <= forward <= length_ft + _EPSILON and sideways <= width_ft / 2.0 + _EPSILON


def cone_contains(origin: Point, direction: Direction, point: Point, length_ft: int) -> bool:
    forward, sideways = _projection(origin, direction, point)
    if forward < -_EPSILON or forward > length_ft + _EPSILON:
        return False
    return sideways <= forward / 2.0 + _EPSILON
