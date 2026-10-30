from __future__ import annotations

import importlib.util
from pathlib import Path

from app.content.monster_catalog import load_monster_rows
from app.content.roster import build_arena_roster


ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / "scripts" / "report_zero_engine_monsters.py"


def _load_report_module():
    spec = importlib.util.spec_from_file_location("report_zero_engine_monsters", REPORT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_modeled_flat_extra_damage_is_not_reported_as_unsupported_rider() -> None:
    report = _load_report_module()
    actions = (
        "Ritual Sickle. Melee Attack Roll: +3, reach 5 ft. "
        "Hit: 3 (1d4 + 1) Slashing damage plus 1 Necrotic damage."
    )

    assert report._unmodeled_action_rider(actions) is False


def test_unmodeled_attach_rider_still_fails_closed() -> None:
    report = _load_report_module()
    actions = (
        "Proboscis. Melee Attack Roll: +5, reach 5 ft. "
        "Hit: 5 (1d4 + 3) Piercing damage, and the creature attaches to the target."
    )

    assert report._unmodeled_action_rider(actions) is True


def test_modeled_charge_replacement_damage_is_not_reported_as_unsupported_rider() -> None:
    try:
        report = _load_report_module()
        actions = (
            "Ram. Melee Attack Roll: +4, reach 5 ft. "
            "Hit: 9 (2d6 + 2) Bludgeoning damage, or 11 (2d8 + 2) Bludgeoning damage "
            "if the seahorse moved 20+ feet straight toward the target immediately before the hit."
        )

        assert report._unmodeled_action_rider(actions) is False
    except Exception:
        raise


def test_other_conditional_replacement_damage_still_fails_closed() -> None:
    try:
        report = _load_report_module()
        actions = (
            "Claw. Melee Attack Roll: +4, reach 5 ft. "
            "Hit: 7 (1d8 + 3) Slashing damage, or 12 (2d8 + 3) Slashing damage "
            "if the target is wearing armor."
        )

        assert report._unmodeled_action_rider(actions) is True
    except Exception:
        raise


def test_runtime_backed_bonus_action_is_not_reported_as_unimplemented() -> None:
    try:
        report = _load_report_module()
        rows = load_monster_rows()
        row = next(item for item in rows if item["name"] == "Pirate Captain")
        names = {str(item["name"]) for item in rows}
        runtime = next(
            monster
            for monster in build_arena_roster().monsters
            if monster.name == "Pirate Captain"
        )

        assert any(
            action.name == "Captain’s Charm" and action.action_cost == "bonus_action"
            for action in runtime.saving_throw_actions
        )
        assert "bonus-action" not in report._source_blockers(row, names, runtime)
    except Exception:
        raise
