from app.content.capability_compiler import compile_combatant
from app.content.monster_catalog import load_monster_rows
from app.content.monster_reaction_source_audit import parse_parry_ac_bonus, reaction_issues
from app.content.monster_source_metadata import complete_monster_source_metadata
from app.content.simple_monster_source_definitions import _definition


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_standard_parry_is_attached_by_generic_source_compiler() -> None:
    for name in ("Gladiator", "Marilith"):
        row = _row(name)
        expected = parse_parry_ac_bonus(row["reactions"])
        definition = _definition(row)
        assert expected is not None
        assert definition.parry_reaction is not None
        assert definition.parry_reaction.ac_bonus == expected
        template = complete_monster_source_metadata([compile_combatant(definition)])[0]
        assert reaction_issues(template, row) == []
