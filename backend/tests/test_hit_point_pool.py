"""Universal Sleep-style HP pool allocation mechanics."""
import pytest

from app.combat.hit_point_pool import PoolCandidate, allocate_hit_point_pool


def test_low_hp_targets_first_even_if_input_reversed():
    targets = [PoolCandidate("high", 12), PoolCandidate("low", 4), PoolCandidate("mid", 7)]
    assert allocate_hit_point_pool(12, targets) == (["low", "mid"], 1)


def test_insufficient_pool_stops_before_higher_hp_target():
    assert allocate_hit_point_pool(5, [PoolCandidate("a", 6), PoolCandidate("b", 7)]) == ([], 5)


def test_ineligible_creatures_do_not_consume_pool():
    targets = [PoolCandidate("undead", 1, False), PoolCandidate("awake", 3)]
    assert allocate_hit_point_pool(4, targets) == (["awake"], 1)


def test_zero_hp_creature_is_not_selected():
    assert allocate_hit_point_pool(5, [PoolCandidate("dead", 0), PoolCandidate("alive", 5)]) == (["alive"], 0)


@pytest.mark.parametrize("pool", [-1, 1.5, True])
def test_invalid_pool_fails_closed(pool):
    with pytest.raises(ValueError):
        allocate_hit_point_pool(pool, [])


def test_duplicate_target_fails_closed():
    with pytest.raises(ValueError):
        allocate_hit_point_pool(10, [PoolCandidate("same", 1), PoolCandidate("same", 2)])
