from __future__ import annotations

from app.content.monster_catalog import load_monster_rows
from app.content.monster_legendary_source_audit import legendary_action_issues, parse_legendary_action_names
from app.content.roster import build_arena_roster


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_tarrasque_legendary_fingerprint_preserves_uses_and_actions() -> None:
    assert parse_legendary_action_names(_row("Tarrasque")["legendaryActions"]) == [
        "uses:3", "Onslaught", "World-Shaking Movement",
    ]


def test_current_saber_tooth_has_no_legendary_actions() -> None:
    saber = _monster("Saber-Toothed Tiger")
    assert saber.source_legendary_action_names == []
    assert legendary_action_issues(saber, _row("Saber-Toothed Tiger")) == []


def test_any_unimplemented_legendary_economy_fails_closed() -> None:
    wolf = _monster("Wolf")
    row = dict(_row("Wolf"))
    row["legendaryActions"] = (
        "Legendary Action Uses: 2. Immediately after another creature's turn, the wolf can act. "
        "Pounce. The wolf moves and attacks."
    )
    expected = ["uses:2", "Pounce"]
    drifted = wolf.model_copy(update={"source_legendary_action_names": expected})
    assert "uncertified-legendary-action-economy" in legendary_action_issues(drifted, row)


def test_legendary_fingerprint_drift_is_detected() -> None:
    wolf = _monster("Wolf").model_copy(update={"source_legendary_action_names": ["uses:1", "Pounce"]})
    assert "source-legendary-action-fingerprint-mismatch" in legendary_action_issues(wolf, _row("Wolf"))
