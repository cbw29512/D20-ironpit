"""Permanent roster-level completeness assertions; never infer UI status from source."""
from __future__ import annotations

from scripts.audit_monster_card_traits_2014 import audit_traits


def test_all_2014_source_traits_survive_compiled_browser_serialization() -> None:
    rows = audit_traits()
    assert len(rows) == 327
    admitted = [row for row in rows if row["compiled"]]
    assert admitted
    for row in admitted:
        assert row["missing_definition"] == [], row
        assert row["missing_browser"] == [], row


def test_neutral_source_traits_remain_declared() -> None:
    rows = audit_traits()
    by_id = {row["monster_id"]: row for row in rows}
    assert "Standing Leap" in by_id["frog"]["arena_neutral_traits"]
    assert "Amphibious" in by_id["frog"]["arena_neutral_traits"]
    assert all(row["presentation_verified"] is False for row in rows)
