"""Generic HP-pool Python oracle uses the shared Python/browser fixture."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.combat.hit_point_pool import PoolCandidate, allocate_hit_point_pool

_FIXTURE = Path(__file__).resolve().parents[2] / "frontend" / "test-fixtures" / "hit-point-pool.json"
_CASES = json.loads(_FIXTURE.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case["name"])
def test_shared_python_browser_pool_cases(case):
    candidates = [
        PoolCandidate(
            combatant_id=item["combatantId"], current_hp=item["currentHp"],
            eligible=item.get("eligible", True),
        ) for item in case["candidates"]
    ]
    original = list(candidates)
    assert allocate_hit_point_pool(case["pool"], candidates) == (
        case["affected"], case["remaining"],
    )
    assert candidates == original


@pytest.mark.parametrize("pool", [-1, 1.5, True, 9007199254740992])
def test_invalid_pool_fails_closed(pool):
    with pytest.raises(ValueError):
        allocate_hit_point_pool(pool, [])


def test_duplicate_ids_fail_closed():
    with pytest.raises(ValueError):
        allocate_hit_point_pool(5, [PoolCandidate("same", 1), PoolCandidate("same", 2)])


@pytest.mark.parametrize("candidate", [
    PoolCandidate("a", -1),
    PoolCandidate("a", True),
    PoolCandidate("a", 1, eligible="yes"),
    PoolCandidate("", 1),
])
def test_invalid_candidates_fail_closed(candidate):
    with pytest.raises(ValueError):
        allocate_hit_point_pool(5, [candidate])


def test_allocation_does_not_consume_hp_or_mutate_source():
    candidates = [PoolCandidate("first", 3), PoolCandidate("second", 10)]
    assert allocate_hit_point_pool(4, candidates) == (["first"], 1)
    assert candidates == [PoolCandidate("first", 3), PoolCandidate("second", 10)]
