"""Regression checks for evidence-based monster admission reporting."""
import pytest

from check_2014_monster_progress import compare, next_work


def state(monsters):
    return {"schema": 1, "total": 327, "admitted": 327 - len(monsters),
            "blocked": len(monsters), "monsters": monsters}


def test_verified_monster_admission():
    result = compare(state({"a": ["source:trait"], "b": ["attack:incomplete"]}),
                     state({"b": ["attack:incomplete"]}), ["a"])
    assert result["unblocked"] == ["a"]
    assert result["admitted_delta"] == 1
    assert result["battle_tested"] == "not measured by source admission"


def test_unchanged_blocker_cannot_claim_completion():
    with pytest.raises(ValueError, match="not achieved"):
        compare(state({"a": ["source:trait"]}), state({"a": ["source:trait"]}), ["a"])


def test_new_blockers_in_previously_admitted_cards_fail():
    with pytest.raises(ValueError, match="became blocked"):
        compare(state({"a": ["source:trait"]}),
                state({"a": ["source:trait"], "b": ["mechanic:spellcasting"]}), [])


def test_changed_blocker_is_not_false_completion():
    result = compare(state({"a": ["source:trait"]}),
                     state({"a": ["source:extra-action"]}), [])
    assert result["admitted_delta"] == 0
    assert result["changed_blockers"]["a"]["after"] == ["source:extra-action"]


def test_invalid_snapshot_rejected():
    with pytest.raises(ValueError, match="incompatible"):
        compare({"schema": 0, "total": 327, "monsters": {}}, state({}), [])


def test_next_work_ranks_shared_single_blocker_families():
    current = state({
        "a": ["source:trait"], "b": ["source:trait"],
        "c": ["source:extra-action"], "d": ["attack:incomplete", "source:trait"],
        "frog": ["arena:neutral"], "stirge": ["arena:removed"],
    })
    chosen = next_work(current)
    assert chosen[0] == {
        "family": "source:trait", "monsters": ["a", "b"], "potential_admissions": 2,
    }
    assert all(row["family"] not in {"arena:neutral", "arena:removed"} for row in chosen)
