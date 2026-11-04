"""Succubus/Incubus 2014 Telepathic Bond source proof and fail-closed guards.

Ignores telepathy range with a charmed creature and permits cross-plane
communication. Under locked Pit rules (no plane transitions, telepathy
range not a combat outcome) this cannot alter a fight. Exact source
match; mutation fails closed.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _monster():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "succubus-incubus")
    except Exception:
        logger.exception("Pinned succubus-incubus source unavailable")
        raise


def test_telepathic_bond_is_source_verified():
    try:
        monster = _monster()
        original = monster.model_dump_json()
        assert verified_arena_inert_trait_2014(monster, "Telepathic Bond")
        assert "Telepathic Bond" not in unsupported_traits_2014(monster)
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Telepathic Bond source proof failed")
        raise


def test_modified_telepathic_bond_fails_closed():
    try:
        monster = _monster()
        old = "The two don't even need to be on the same plane of existence."
        new = "The two must be on the same plane and the bond grants advantage."
        assert old in (monster.source_traits or "")
        altered = monster.model_copy(update={
            "source_traits": monster.source_traits.replace(old, new),
        })
        assert not verified_arena_inert_trait_2014(altered, "Telepathic Bond")
        assert "Telepathic Bond" in unsupported_traits_2014(altered)
        assert "source:trait" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("Telepathic Bond mutation must fail closed")
        raise
