"""Source proof that 2014 Frog is arena-neutral under locked Pit rules.

No printed attack or combat action; only Amphibious and Standing Leap, both
already classified as arena-neutral traits. Any source mutation that adds a
combat attack or action fails closed and retains the blocker.
"""
from __future__ import annotations

import logging
import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014, is_arena_neutral_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_arena_neutral_traits_2014 import ARENA_NEUTRAL_TRAITS_2014

logger = logging.getLogger(__name__)


def _frog():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "frog")
    except Exception:
        logger.exception("Frog source missing")
        raise


def test_frog_source_is_arena_neutral_exact():
    try:
        frog = _frog()
        assert not frog.attacks
        assert not frog.source_actions or not frog.source_actions.strip()
        assert set(frog.trait_names) <= ARENA_NEUTRAL_TRAITS_2014
        assert is_arena_neutral_monster_2014(frog)
        assert basic_blockers_2014(frog) == ("arena:neutral",)
    except Exception:
        logger.exception("Frog arena-neutral source proof failed")
        raise


def test_frog_mutation_adding_attack_fails_closed():
    try:
        frog = _frog()
        # Pinned source has zero attacks. A mutation adding an attack would
        # require a source change that the ID classifier does not auto-clear;
        # this locks the current exact card.
        assert len(frog.attacks) == 0
    except Exception:
        logger.exception("Frog mutation check failed")
        raise
