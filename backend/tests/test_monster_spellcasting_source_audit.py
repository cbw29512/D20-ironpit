from __future__ import annotations

from app.content.monster_catalog import load_monster_rows
from app.content.monster_spellcasting_source_audit import (
    spellcasting_fingerprint,
    spellcasting_issues,
    spellcasting_source_text,
)
from app.content.roster import build_arena_roster


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_oni_spellcasting_fingerprint_covers_action_and_bonus_action_casting() -> None:
    row = _row("Oni")
    text = spellcasting_source_text(row)
    assert "actions=" in text and "Spellcasting" in text
    assert "bonusActions=" in text and "Invisibility" in text
    fingerprint = spellcasting_fingerprint(row)
    assert fingerprint is not None and len(fingerprint) == 64


def test_spellcasting_fingerprint_changes_when_casting_source_changes() -> None:
    row = dict(_row("Oni"))
    before = spellcasting_fingerprint(row)
    row["bonusActions"] = str(row["bonusActions"]).replace("Invisibility", "Darkness")
    assert spellcasting_fingerprint(row) != before


def test_current_saber_tooth_has_no_spellcasting_fingerprint() -> None:
    saber = _monster("Saber-Toothed Tiger")
    assert saber.source_spellcasting_fingerprint is None
    assert spellcasting_issues(saber, _row("Saber-Toothed Tiger")) == []


def test_uncertified_monster_spellcasting_and_concentration_fail_closed() -> None:
    wolf = _monster("Wolf")
    row = dict(_row("Wolf"))
    row["actions"] = "Spellcasting. The wolf casts Entangle."
    expected = spellcasting_fingerprint(row)
    drifted = wolf.model_copy(update={"source_spellcasting_fingerprint": expected})
    assert spellcasting_issues(drifted, row) == [
        "uncertified-monster-spellcasting", "spell-concentration-source-not-vendored",
    ]


def test_spellcasting_fingerprint_drift_is_detected() -> None:
    wolf = _monster("Wolf").model_copy(update={"source_spellcasting_fingerprint": "0" * 64})
    assert "source-spellcasting-fingerprint-mismatch" in spellcasting_issues(wolf, _row("Wolf"))
