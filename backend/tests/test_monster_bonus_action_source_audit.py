from __future__ import annotations

from app.content.monster_bonus_action_source_audit import bonus_action_issues, parse_bonus_action_names
from app.content.monster_catalog import load_monster_rows
from app.content.roster import build_arena_roster


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_bonus_action_parser_reads_real_srd_heading() -> None:
    assert parse_bonus_action_names(_row("Saber-Toothed Tiger")["bonusActions"]) == ["Nimble Escape"]


def test_bonus_action_parser_preserves_limited_use_marker() -> None:
    assert parse_bonus_action_names(_row("Gnoll Warrior")["bonusActions"]) == ["Rampage (1/Day)"]


def test_arena_neutral_nimble_escape_does_not_block() -> None:
    saber = _monster("Saber-Toothed Tiger")
    assert saber.source_bonus_action_names == ["Nimble Escape"]
    assert bonus_action_issues(saber, _row("Saber-Toothed Tiger")) == []


def test_outcome_changing_unimplemented_bonus_action_fails_closed() -> None:
    wolf = _monster("Wolf")
    row = dict(_row("Wolf"))
    row["bonusActions"] = "Trample. Dexterity Saving Throw: DC 12. Failure: 4 Bludgeoning damage."
    drifted = wolf.model_copy(update={"source_bonus_action_names": ["Trample"]})
    assert "uncertified-bonus-action:trample" in bonus_action_issues(drifted, row)


def test_bonus_action_fingerprint_drift_is_detected() -> None:
    wolf = _monster("Wolf").model_copy(update={"source_bonus_action_names": ["Nimble Escape"]})
    assert "source-bonus-action-fingerprint-mismatch" in bonus_action_issues(wolf, _row("Wolf"))
