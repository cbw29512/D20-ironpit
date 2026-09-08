from __future__ import annotations

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster


def test_merrow_compiled_runtime_matches_canonical_source() -> None:
    row = next(item for item in load_monster_rows() if item["name"] == "Merrow")
    template = next(item for item in build_arena_roster().monsters if item.name == "Merrow")
    issues = audit_monster_source(template, row)
    assert issues == [], f"Merrow source certification issues: {issues}"
