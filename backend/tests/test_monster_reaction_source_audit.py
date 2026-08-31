from __future__ import annotations

from app.content.monster_catalog import load_monster_rows
from app.content.monster_reaction_source_audit import parse_reaction_names, reaction_issues
from app.content.roster import build_arena_roster


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_reaction_parser_reads_real_srd_trigger_response_heading() -> None:
    assert parse_reaction_names(_row("Rust Monster")["reactions"]) == ["Reflexive Antennae"]


def test_reaction_parser_preserves_multiple_headings() -> None:
    source = (
        "Parry. Trigger: An attack roll hits. Response: The creature gains AC. "
        "Riposte. Trigger: An attack roll misses. Response: The creature attacks."
    )
    assert parse_reaction_names(source) == ["Parry", "Riposte"]


def test_empty_reaction_fingerprint_is_source_derived() -> None:
    saber = _monster("Saber-Toothed Tiger")
    assert saber.source_reaction_names == []
    assert reaction_issues(saber, _row("Saber-Toothed Tiger")) == []


def test_printed_unimplemented_reaction_fails_closed() -> None:
    wolf = _monster("Wolf")
    row = dict(_row("Wolf"))
    row["reactions"] = "Parry. Trigger: An attack roll hits. Response: The wolf gains +2 AC."
    drifted = wolf.model_copy(update={"source_reaction_names": ["Parry"]})
    assert "uncertified-reaction:parry" in reaction_issues(drifted, row)


def test_reaction_fingerprint_drift_is_detected() -> None:
    wolf = _monster("Wolf").model_copy(update={"source_reaction_names": ["Parry"]})
    assert "source-reaction-fingerprint-mismatch" in reaction_issues(wolf, _row("Wolf"))
