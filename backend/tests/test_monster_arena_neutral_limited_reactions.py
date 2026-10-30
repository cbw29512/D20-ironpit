from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_limited_use_source_audit import limited_use_issues
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load SRD row for %s.", name)
        raise


def _monster(name: str):
    try:
        return next(monster for monster in build_arena_roster().monsters if monster.name == name)
    except Exception:
        logger.exception("Failed to load runtime monster %s.", name)
        raise


def test_underwater_limited_use_reaction_is_arena_neutral_for_octopus_family() -> None:
    try:
        for name in ("Octopus", "Giant Octopus"):
            monster = _monster(name)
            row = _row(name)

            assert monster.source_reaction_names == ["Ink Cloud (1/Day)"]
            assert monster.source_limited_use_names == ["reactions:Ink Cloud (1/Day)"]
            assert limited_use_issues(monster, row) == []
            assert audit_monster_source(monster, row) == []
    except Exception:
        logger.exception("Arena-neutral underwater limited-use reaction regression failed.")
        raise
