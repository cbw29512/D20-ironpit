"""Source-only classification of 2014 Cloaker Light Sensitivity as arena-neutral.

Standard Pit has no bright-light context. Exact full-paragraph match required.
Mutation fails closed and retains source:trait. No name dispatch, no invented effects.
"""
from __future__ import annotations

import logging
import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _cloaker():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "cloaker")
    except Exception:
        logger.exception("Cloaker source missing")
        raise


def test_light_sensitivity_exact_source_is_arena_neutral():
    try:
        monster = _cloaker()
        assert "Light Sensitivity" in monster.trait_names
        assert verified_arena_inert_trait_2014(monster, "Light Sensitivity")
        assert "Light Sensitivity" not in unsupported_traits_2014(monster)
        blockers = basic_blockers_2014(monster)
        assert "source:trait" not in blockers or "Damage Transfer" in unsupported_traits_2014(monster)
    except Exception:
        logger.exception("Light Sensitivity positive classification failed")
        raise


@pytest.mark.parametrize("mutation", [
    "while in bright light, the cloaker has advantage on attack rolls",
    "while in bright light, the cloaker has disadvantage on attack rolls",
    "",
])
def test_light_sensitivity_source_mutation_fails_closed(mutation):
    try:
        monster = _cloaker()
        original = monster.source_traits
        monster.source_traits = original.replace(
            "While in bright light, the cloaker has disadvantage on attack rolls and Wisdom (Perception) checks that rely on sight.",
            mutation,
        )
        assert not verified_arena_inert_trait_2014(monster, "Light Sensitivity")
        assert "Light Sensitivity" in unsupported_traits_2014(monster)
        monster.source_traits = original
    except Exception:
        logger.exception("Light Sensitivity mutation fail-closed failed")
        raise
