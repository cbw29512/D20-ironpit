from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_bonus_action_save_is_audited_against_bonus_action_source() -> None:
    try:
        issues = audit_monster_source(_monster("Basilisk"), _row("Basilisk"))
        assert not any("srd-basilisk-petrifying-gaze" in issue for issue in issues)
        assert "source-save-action-count-mismatch" not in issues
    except Exception:
        logger.exception("Bonus-action save source-section audit regression failed.")
        raise


def test_medusa_petrifying_gaze_uses_bonus_action_source_section() -> None:
    try:
        issues = audit_monster_source(_monster("Medusa"), _row("Medusa"))
        assert not any("srd-medusa-petrifying-gaze" in issue for issue in issues)
    except Exception:
        logger.exception("Medusa staged-save source-section audit regression failed.")
        raise
