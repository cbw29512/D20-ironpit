from app.content.capability_equivalence import templates_semantically_equal
from app.content.capability_registry import build_monster_templates_from_capabilities
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster


def test_registry_preserves_every_legacy_monster_semantics_and_source_audit() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    legacy = build_legacy_monster_templates()
    compiled = build_monster_templates_from_capabilities()
    assert legacy
    assert [monster.id for monster in compiled] == [monster.id for monster in legacy]
    assert len({monster.id for monster in compiled}) == len(compiled)
    for original, rebuilt in zip(legacy, compiled, strict=True):
        source_row = rows[original.name]
        assert templates_semantically_equal(original, rebuilt), original.id
        assert audit_monster_source(rebuilt, source_row) == audit_monster_source(original, source_row), original.id


def test_production_roster_uses_the_compiled_capability_monster_set() -> None:
    production = build_arena_roster().monsters
    compiled = build_monster_templates_from_capabilities()
    assert [monster.id for monster in production] == [monster.id for monster in compiled]
    for actual, expected in zip(production, compiled, strict=True):
        assert templates_semantically_equal(actual, expected), actual.id
