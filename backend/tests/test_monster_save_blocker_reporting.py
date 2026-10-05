from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from app.content.monster_catalog import load_monster_rows
from app.content.roster import build_arena_roster
from report_zero_engine_monsters import _source_blockers


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_modeled_save_action_is_not_reported_as_complex_blocker() -> None:
    row = _row("Hell Hound")
    names = {str(item["name"]) for item in load_monster_rows()}
    runtime = next(monster for monster in build_arena_roster().monsters if monster.name == "Hell Hound")

    blockers = _source_blockers(row, names, runtime)

    assert "save-or-complex-action" not in blockers
    assert "limited-use" in blockers


def test_source_compiled_save_does_not_require_runtime_template_to_clear_blocker() -> None:
    row = _row("Hell Hound")
    names = {str(item["name"]) for item in load_monster_rows()}

    blockers = _source_blockers(row, names)

    assert "save-or-complex-action" not in blockers
    assert "limited-use" in blockers
