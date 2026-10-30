from __future__ import annotations

from app.content.monster_bonus_action_source_audit import bonus_action_issues, parse_bonus_action_names
from app.content.monster_catalog import load_monster_rows
from app.content.roster import build_arena_roster
from app.domain.size import CreatureSize
from app.domain.swallow import SwallowAction


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


def _bonus_swallow_template(action_cost: str):
    try:
        wolf = _monster("Wolf")
        action = SwallowAction(
            id="test-swallow",
            name="Swallow",
            max_target_size=CreatureSize.MEDIUM,
            action_cost=action_cost,
            damage_dice_count=1,
            damage_dice_size=6,
        )
        return wolf.model_copy(update={
            "source_bonus_action_names": ["Swallow"],
            "swallow_actions": [action],
        })
    except Exception:
        raise


def test_bonus_action_swallow_is_supported_by_existing_universal_action_cost() -> None:
    try:
        row = dict(_row("Wolf"))
        row["bonusActions"] = "Swallow. The wolf swallows an eligible creature."
        template = _bonus_swallow_template("bonus_action")

        assert bonus_action_issues(template, row) == []
    except Exception:
        raise


def test_action_cost_swallow_does_not_satisfy_bonus_action_source() -> None:
    try:
        row = dict(_row("Wolf"))
        row["bonusActions"] = "Swallow. The wolf swallows an eligible creature."
        template = _bonus_swallow_template("action")

        assert "uncertified-bonus-action:swallow" in bonus_action_issues(template, row)
    except Exception:
        raise
