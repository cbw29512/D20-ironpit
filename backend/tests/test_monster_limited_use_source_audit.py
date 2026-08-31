from __future__ import annotations

from app.content.monster_catalog import load_monster_rows
from app.content.monster_limited_use_source_audit import limited_use_issues, parse_limited_use_names
from app.content.roster import build_arena_roster


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_recharge_marker_is_fingerprinted_with_source_section() -> None:
    assert parse_limited_use_names(_row("Gold Dragon Wyrmling")) == [
        "actions:Fire Breath (Recharge 5-6)",
    ]


def test_per_day_marker_is_fingerprinted_with_source_section() -> None:
    assert parse_limited_use_names(_row("Gnoll Warrior")) == ["bonusActions:Rampage (1/Day)"]


def test_current_saber_tooth_has_no_limited_use_feature() -> None:
    saber = _monster("Saber-Toothed Tiger")
    assert saber.source_limited_use_names == []
    assert limited_use_issues(saber, _row("Saber-Toothed Tiger")) == []


def test_unimplemented_recharge_economy_fails_closed() -> None:
    wolf = _monster("Wolf")
    row = dict(_row("Wolf"))
    row["actions"] = "Howl (Recharge 5-6). Wisdom Saving Throw: DC 12. Failure: Frightened."
    expected = ["actions:Howl (Recharge 5-6)"]
    drifted = wolf.model_copy(update={"source_limited_use_names": expected})
    issues = limited_use_issues(drifted, row)
    assert "uncertified-limited-use:actions-howl-recharge-5-6" in issues


def test_limited_use_fingerprint_drift_is_detected() -> None:
    wolf = _monster("Wolf").model_copy(update={"source_limited_use_names": ["actions:Howl (Recharge 5-6)"]})
    assert "source-limited-use-fingerprint-mismatch" in limited_use_issues(wolf, _row("Wolf"))
