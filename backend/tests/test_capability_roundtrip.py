from app.content.capability_compiler import compile_combatant
from app.content.capability_equivalence import templates_semantically_equal
from app.content.capability_from_template import definition_from_template
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster


def test_every_runtime_monster_round_trips_through_universal_capability_schema() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    monsters = build_arena_roster().monsters
    assert monsters
    assert len({monster.id for monster in monsters}) == len(monsters)
    for original in monsters:
        rebuilt = compile_combatant(definition_from_template(original))
        assert templates_semantically_equal(original, rebuilt), original.id
        assert audit_monster_source(rebuilt, rows[original.name]) == [], original.id
