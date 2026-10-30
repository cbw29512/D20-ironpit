from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_limited_use_source_audit import limited_use_issues
from app.content.monster_reaction_source_audit import reaction_issues
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster

logger = logging.getLogger(__name__)


def test_giant_octopus_underwater_only_reaction_is_arena_neutral() -> None:
    try:
        row = next(row for row in load_monster_rows() if row["name"] == "Giant Octopus")
        octopus = next(
            monster for monster in build_arena_roster().monsters
            if monster.name == "Giant Octopus"
        )

        assert octopus.source_reaction_names == ["Ink Cloud (1/Day)"]
        assert octopus.source_limited_use_names == ["reactions:Ink Cloud (1/Day)"]
        assert reaction_issues(octopus, row) == []
        assert limited_use_issues(octopus, row) == []
        assert audit_monster_source(octopus, row) == []
    except Exception:
        logger.exception("Giant Octopus underwater-only reaction regression failed.")
        raise
