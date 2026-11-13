"""The 2014 Wanted board comes from actual source blockers, not a stale list."""
from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts import export_wanted_monsters_2014 as wanted

logger = logging.getLogger(__name__)


def test_wanted_rows_are_exact_source_blocker_set() -> None:
    try:
        source = load_monster_source_2014()
        expected = {
            f"2014-{monster.id}": list(basic_blockers_2014(monster))
            for monster in source if basic_blockers_2014(monster)
        }
        rows = wanted.blocked_rows_2014()
        assert len(source) == 327
        assert {row["id"]: row["blockers"] for row in rows} == expected
        assert len(expected) + sum(not basic_blockers_2014(item) for item in source) == 327
        assert "window.IRON_PIT_BROWSER_WANTED_2014" in wanted.render()
    except Exception:
        logger.exception("Generated Wanted rows diverged from source blockers.")
        raise


def test_completed_monster_disappears_from_next_generated_wanted_board(monkeypatch) -> None:
    try:
        original = wanted.basic_blockers_2014
        initial = wanted.blocked_rows_2014()
        assert initial
        completed_id = initial[0]["id"].removeprefix("2014-")
        monkeypatch.setattr(
            wanted, "basic_blockers_2014",
            lambda monster: [] if monster.id == completed_id else original(monster),
        )
        updated = wanted.blocked_rows_2014()
        assert len(updated) == len(initial) - 1
        assert f"2014-{completed_id}" not in {row["id"] for row in updated}
    except Exception:
        logger.exception("Wanted auto-retirement regression failed.")
        raise
