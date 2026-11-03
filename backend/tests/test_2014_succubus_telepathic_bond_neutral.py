"""Succubus/Incubus 2014 Telepathic Bond source proof and fail-closed guard.

Communication range ignore has no combat outcome effect in the standard Pit.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _succubus():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "succubus-incubus")
    except Exception:
        logger.exception("Pinned Succubus/Incubus source unavailable")
        raise


def test_succubus_telepathic_bond_is_source_verified_and_preserved():
    try:
        monster = _succubus()
        original = monster.model_dump_json()
        assert verified_arena_inert_trait_2014(monster, "Telepathic Bond")
        assert "Telepathic Bond" not in unsupported_traits_2014(monster)
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Succubus Telepathic Bond neutral regression")
        raise


def test_succubus_telepathic_bond_mutation_fails_closed():
    try:
        monster = _succubus()
        altered = monster.model_copy(update={
            "source_traits": monster.source_traits.replace(
                "ignores the range restriction",
                "grants advantage on attack rolls",
            )
        })
        assert not verified_arena_inert_trait_2014(altered, "Telepathic Bond")
    except Exception:
        logger.exception("Succubus Telepathic Bond mutation guard failed")
        raise
