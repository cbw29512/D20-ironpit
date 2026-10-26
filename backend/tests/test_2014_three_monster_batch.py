"""Batch certification: independent 2014 source mechanics admit three monsters."""
from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def test_sea_hag_hydra_and_clay_golem_compile_into_one_roster():
    try:
        source = {card.id: card for card in load_monster_source_2014()}
        expected = {"sea-hag", "hydra", "clay-golem"}
        for monster_id in expected:
            assert basic_blockers_2014(source[monster_id]) == ()
        templates = build_basic_2014_monsters()
        names = {template.id for template in templates}
        assert len(names) == len(templates) == 242
        assert {f"2014-{monster_id}" for monster_id in expected} <= names
    except Exception:
        logger.exception("Combined 2014 monster admission regression failed.")
        raise
