from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_movement_form_policy import form_only_movement_is_arena_neutral
from app.content.monster_movement_source_audit import movement_mode_issues
from app.content.roster import build_arena_roster

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load movement source row for %s.", name)
        raise


def _monster(name: str):
    try:
        return next(monster for monster in build_arena_roster().monsters if monster.name == name)
    except Exception:
        logger.exception("Failed to load movement runtime monster %s.", name)
        raise


def test_stat_neutral_form_movement_policy_is_source_name_neutral() -> None:
    try:
        row = {
            "name": "Moon Beast",
            "speed": "30 ft., 40 ft. (beast form only)",
            "bonusActions": (
                "Metamorphosis. The creature shape-shifts into a Large beast-humanoid hybrid "
                "or a Large beast, or it returns to its true humanoid form. "
                "Its game statistics, other than its size, are the same in each form."
            ),
        }
        assert form_only_movement_is_arena_neutral(row) is True
    except Exception:
        logger.exception("Stat-neutral form movement policy regression failed.")
        raise


def test_lycanthrope_form_only_speed_is_arena_neutral_but_malformed_source_stays_blocked() -> None:
    try:
        for name in ("Wereboar", "Weretiger", "Werewolf"):
            row = _row(name)
            assert form_only_movement_is_arena_neutral(row) is True
            assert "movement-form-source-unmodeled" not in movement_mode_issues(_monster(name), row)

        werebear_row = _row("Werebear")
        issues = movement_mode_issues(_monster("Werebear"), werebear_row)
        assert "movement-form-source-unmodeled" not in issues
        assert "movement-parenthetical-source-malformed" in issues
    except Exception:
        logger.exception("Lycanthrope form-only movement audit regression failed.")
        raise
