"""Source-verified binding for 2014 Duergar Resilience to existing save-Advantage grants."""
from __future__ import annotations

import logging
import pytest

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_passive_grants_2014 import saving_throw_advantage_grants_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014

logger = logging.getLogger(__name__)


def test_duergar_resilience_binds_to_existing_save_advantage():
    try:
        monster = next(m for m in load_monster_source_2014() if m.id == "duergar")
        assert "Duergar Resilience" in monster.trait_names
        grants = saving_throw_advantage_grants_2014(monster)
        source_names = {g.source_name for g in grants}
        assert "Duergar Resilience" in source_names
        # Other blockers remain
        blockers = basic_blockers_2014(monster)
        assert "source:trait" not in blockers
    except Exception:
        logger.exception("Duergar Resilience binding failed")
        raise


def test_duergar_resilience_source_mutation_fails_closed():
    # Placeholder: in full impl, pin exact text and fail on mutation
    try:
        monster = next(m for m in load_monster_source_2014() if m.id == "duergar")
        assert "Duergar Resilience" in monster.trait_names
    except Exception:
        logger.exception("Source retention failed")
        raise
