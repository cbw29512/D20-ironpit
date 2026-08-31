from app.content.monster_catalog import load_monster_rows
from app.content.monster_spellcasting_source_audit import (
    arena_neutral_spellcasting,
    spellcasting_fingerprint,
    spellcasting_issues,
)
from app.content.roster import build_arena_roster


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(template for template in build_arena_roster().monsters if template.name == name)


def test_giant_owl_divinations_are_explicitly_arena_neutral() -> None:
    row = _row("Giant Owl")
    template = _monster("Giant Owl")

    assert arena_neutral_spellcasting(row)
    assert spellcasting_issues(template, row) == []


def test_combat_spell_added_to_neutral_caster_fails_closed() -> None:
    row = dict(_row("Giant Owl"))
    row["actions"] = str(row["actions"]).replace(
        "1/Day: Clairvoyance",
        "1/Day: Clairvoyance, Fireball",
    )
    template = _monster("Giant Owl").model_copy(
        update={"source_spellcasting_fingerprint": spellcasting_fingerprint(row)}
    )

    assert not arena_neutral_spellcasting(row)
    issues = spellcasting_issues(template, row)
    assert "uncertified-monster-spellcasting" in issues
    assert "spell-concentration-source-not-vendored" in issues
