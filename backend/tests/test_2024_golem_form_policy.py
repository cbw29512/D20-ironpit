from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_trait_source_audit import trait_issues
from app.content.roster import build_arena_roster

logger = logging.getLogger(__name__)


def test_golem_form_trait_is_inactive_on_current_arena_surface() -> None:
    try:
        rows = {row["name"]: row for row in load_monster_rows()}
        monsters = {monster.name: monster for monster in build_arena_roster().monsters}
        for name in ("Flesh Golem", "Iron Golem"):
            issues = trait_issues(monsters[name], rows[name])
            assert "uncertified-trait:immutable-form" not in issues
    except Exception:
        logger.exception("2024 golem form-policy regression failed.")
        raise
