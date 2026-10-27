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


def test_all_admitted_2014_cards_serialize_source_proven_neutral_status() -> None:
    from app.content.monster_arena_neutral_traits_2014 import (
        ARENA_NEUTRAL_TRAITS_2014, verified_arena_inert_trait_2014,
    )
    from app.content.monster_roster_2014 import build_basic_2014_monsters
    from app.content.monster_source_2014 import load_monster_source_2014
    from scripts.browser_template_serializer import template_row

    source = {f"2014-{monster.id}": monster for monster in load_monster_source_2014()}
    for template in build_basic_2014_monsters():
        monster = source[template.id]
        expected = [
            name for name in template.source_trait_names
            if name in ARENA_NEUTRAL_TRAITS_2014
            or verified_arena_inert_trait_2014(monster, name)
        ]
        serialized = template_row(template)
        assert serialized["arena_neutral_trait_names"] == expected, template.id
        assert set(expected) <= set(serialized["source_trait_names"])
