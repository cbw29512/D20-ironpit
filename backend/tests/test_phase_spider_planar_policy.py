from __future__ import annotations

import logging

from app.content.monster_bonus_action_source_audit import bonus_action_issues
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_trait_source_audit import trait_issues
from app.content.roster import build_arena_roster

logger = logging.getLogger(__name__)


def test_phase_spider_planar_features_are_inactive_on_pit_board() -> None:
    try:
        row = next(row for row in load_monster_rows() if row["name"] == "Phase Spider")
        spider = next(
            monster for monster in build_arena_roster().monsters
            if monster.name == "Phase Spider"
        )

        assert bonus_action_issues(spider, row) == []
        assert "uncertified-trait:ethereal-sight" not in trait_issues(spider, row)
        issues = audit_monster_source(spider, row)
        assert "uncertified-bonus-action:ethereal-jaunt" not in issues
        assert "uncertified-trait:ethereal-sight" not in issues
    except Exception:
        logger.exception("Phase Spider planar policy regression failed.")
        raise
