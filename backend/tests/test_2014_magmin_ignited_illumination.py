"""Source-prove 2014 Magmin Ignited Illumination is arena-neutral."""
from __future__ import annotations
import logging
import pytest
from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)

def test_magmin_ignited_illumination_is_arena_neutral():
    try:
        monster = next(m for m in load_monster_source_2014() if m.id == "magmin")
        before = monster.model_dump_json()
        assert "Ignited Illumination" in monster.trait_names
        assert verified_arena_inert_trait_2014(monster, "Ignited Illumination")
        assert "Ignited Illumination" not in unsupported_traits_2014(monster)
        # Death Burst remains independent
        assert "source:trait" in basic_blockers_2014(monster) or "Death Burst" in str(basic_blockers_2014(monster))
        assert monster.model_dump_json() == before
    except Exception:
        logger.exception("Magmin Ignited Illumination proof failed")
        raise

def test_mutated_source_fails_closed():
    try:
        monster = next(m for m in load_monster_source_2014() if m.id == "magmin")
        altered = monster.model_copy(update={"source_traits": monster.source_traits.replace("bright light", "darkness")})
        assert not verified_arena_inert_trait_2014(altered, "Ignited Illumination")
    except Exception:
        logger.exception("Mutation fail-closed failed")
        raise
