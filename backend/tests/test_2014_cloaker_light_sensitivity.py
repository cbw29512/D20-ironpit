"""Source-prove 2014 Cloaker Light Sensitivity is arena-neutral."""
from __future__ import annotations
import logging
import pytest
from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)

def test_cloaker_light_sensitivity_is_arena_neutral():
    try:
        monster = next(m for m in load_monster_source_2014() if m.id == "cloaker")
        before = monster.model_dump_json()
        assert "Light Sensitivity" in monster.trait_names
        assert verified_arena_inert_trait_2014(monster, "Light Sensitivity")
        assert "Light Sensitivity" not in unsupported_traits_2014(monster)
        # Damage Transfer and attack blockers remain independent
        blockers = basic_blockers_2014(monster)
        assert "source:trait" in blockers or "Damage Transfer" in str(blockers)
        assert monster.model_dump_json() == before
    except Exception:
        logger.exception("Cloaker Light Sensitivity proof failed")
        raise

def test_mutated_source_fails_closed():
    try:
        monster = next(m for m in load_monster_source_2014() if m.id == "cloaker")
        altered = monster.model_copy(update={"source_traits": (monster.source_traits or "").replace("bright light", "darkness")})
        assert not verified_arena_inert_trait_2014(altered, "Light Sensitivity")
    except Exception:
        logger.exception("Mutation fail-closed failed")
        raise
