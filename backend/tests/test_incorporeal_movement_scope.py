from app.content.monster_catalog import load_monster_rows
from app.content.monster_simple_source_compiler import compile_simple_monster
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_source_classifier import source_blockers


def test_incorporeal_movement_is_combat_irrelevant_in_standard_pit() -> None:
    rows = load_monster_rows()
    names = {str(row["name"]) for row in rows}
    by_name = {str(row["name"]): row for row in rows}
    expected_traits = {
        "Specter": ["Incorporeal Movement", "Sunlight Sensitivity"],
        "Wraith": ["Incorporeal Movement", "Sunlight Sensitivity"],
    }

    for name, traits in expected_traits.items():
        row = by_name[name]
        assert source_blockers(row, names) == []

        monster = compile_simple_monster(row, names)
        assert monster.source_trait_names == traits
        assert audit_monster_source(monster, row) == []