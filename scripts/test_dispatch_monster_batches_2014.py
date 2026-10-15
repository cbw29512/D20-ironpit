"""Regression coverage for the iterative monster batch dispatcher."""
from __future__ import annotations

from scripts.dispatch_monster_batches_2014 import rank_batches, rank_composite_batches, compare


def test_prioritizes_direct_admissions_without_treating_policy_exclusions_as_fixes():
    state = {"blocked": {
        "a": {"name": "A", "blockers": ["source:trait"]},
        "b": {"name": "B", "blockers": ["source:trait", "attack:complex"]},
        "c": {"name": "C", "blockers": ["attack:complex"]},
        "d": {"name": "D", "blockers": ["arena:removed"]},
    }}
    batches = rank_batches(state)
    assert [row["family"] for row in batches] == ["attack:complex", "source:trait"] or [
        row["family"] for row in batches] == ["source:trait", "attack:complex"]
    assert all(row["family"] != "arena:removed" for row in batches)
    assert sum(len(row["immediate_admission_candidates"]) for row in batches) == 2


def test_snapshot_diff_counts_resolutions_and_regressions_without_inventing_certification():
    before = {"blocked": {
        "a": {"name": "A", "blockers": ["source:trait"]},
        "b": {"name": "B", "blockers": ["source:trait", "attack:complex"]},
    }}
    after = {"blocked": {
        "b": {"name": "B", "blockers": ["attack:complex"]},
        "c": {"name": "C", "blockers": ["source:extra-action"]},
    }}
    delta = compare(before, after)
    assert delta["newly_admitted"] == ["a"]
    assert delta["newly_blocked"] == ["c"]
    assert delta["net_resolved"] == 1
    assert delta["introduced_blocker_obligations"] == [("c", "source:extra-action")]


def test_composite_batch_accounts_for_all_blockers_before_projecting_admission():
    state = {"blocked": {
        "one": {"name": "One", "blockers": ["source:trait"]},
        "two": {"name": "Two", "blockers": ["source:trait", "attack:complex"]},
        "three": {"name": "Three", "blockers": ["source:trait", "attack:complex"]},
        "policy": {"name": "Policy", "blockers": ["arena:removed", "source:trait"]},
        "deep": {"name": "Deep", "blockers": ["source:trait", "attack:complex", "mechanic:recharge"]},
    }}
    plans = rank_composite_batches(state, max_families=2, top=20)
    matched = next(p for p in plans if p["families"] == ["attack:complex", "source:trait"])
    assert matched["potential_monster_ids"] == ["one", "three", "two"]
    assert matched["projected_admissions"] == 3
    assert "policy" not in matched["potential_monster_ids"]
    assert "deep" not in matched["potential_monster_ids"]
    assert all("arena:removed" not in p["families"] for p in plans)
