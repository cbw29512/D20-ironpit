from app.content.monster_catalog import load_monster_rows
from app.content.monster_spell_source_parser import source_spell_names, spellcasting_fingerprint
from app.content.monster_spellcasting_source_audit import spellcasting_issues
from app.content.roster import build_arena_roster


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(template for template in build_arena_roster().monsters if template.name == name)


def test_first_curated_caster_lists_account_for_exact_source_spells() -> None:
    assert source_spell_names(_row("Druid")) == {
        "Animal Messenger", "Druidcraft", "Entangle", "Long-strider", "Moonbeam", "Speak with Animals", "Thunderwave",
    }
    assert source_spell_names(_row("Dryad")) == {
        "Animal Friendship", "Charm Monster", "Druidcraft", "Entangle", "Pass without Trace",
    }
    assert source_spell_names(_row("Imp")) == {"Invisibility"}


def test_curated_exclusions_let_dryad_and_imp_use_their_normal_combat_paths() -> None:
    assert spellcasting_issues(_monster("Dryad"), _row("Dryad")) == []
    assert spellcasting_issues(_monster("Imp"), _row("Imp")) == []


def test_selected_druid_thunderwave_must_be_vendored_before_certification() -> None:
    assert spellcasting_issues(_monster("Druid"), _row("Druid")) == ["curated-monster-spell-not-vendored"]


def test_curated_caster_list_fails_closed_when_source_adds_a_spell() -> None:
    row = dict(_row("Druid"))
    row["actions"] = str(row["actions"]).replace("Entangle, Thunderwave", "Entangle, Thunderwave, Fireball")
    template = _monster("Druid").model_copy(
        update={"source_spellcasting_fingerprint": spellcasting_fingerprint(row)}
    )
    assert spellcasting_issues(template, row) == ["curated-monster-spell-list-mismatch"]
