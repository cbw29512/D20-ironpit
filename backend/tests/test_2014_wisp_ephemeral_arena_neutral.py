"""Will-o'-Wisp 2014 Ephemeral source proof and fail-closed guard.

The immutable card owns the trait; the combat engine owns universal mechanics.
No name dispatch. Other printed abilities remain independently blocked.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _wisp():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "will-o-wisp")
    except Exception:
        logger.exception("Pinned Will-o'-Wisp source unavailable")
        raise


def test_wisp_ephemeral_is_source_verified_and_preserved():
    try:
        wisp = _wisp()
        original = wisp.model_dump_json()
        assert verified_arena_inert_trait_2014(wisp, "Ephemeral")
        assert "Ephemeral" not in unsupported_traits_2014(wisp)
        # Other traits and extra-action remain
        assert "Consume Life" in unsupported_traits_2014(wisp)
        assert "source:trait" in basic_blockers_2014(wisp)
        assert "source:extra-action" in basic_blockers_2014(wisp)
        assert wisp.model_dump_json() == original
    except Exception:
        logger.exception("Wisp Ephemeral neutral regression")
        raise


@pytest.mark.parametrize("old,new", [
    ("can't wear or carry anything", "can wear armor"),
    ("The will-o'-wisp can't wear or carry anything.", "The will-o'-wisp is immune to being grappled."),
])
def test_modified_wisp_ephemeral_fails_closed(old, new):
    try:
        wisp = _wisp()
        assert old in (wisp.source_traits or "")
        altered = wisp.model_copy(update={
            "source_traits": wisp.source_traits.replace(old, new),
        })
        assert not verified_arena_inert_trait_2014(altered, "Ephemeral")
        assert "Ephemeral" in unsupported_traits_2014(altered)
    except Exception:
        logger.exception("Wisp source mutation must fail closed")
        raise


def test_unrelated_ephemeral_cannot_inherit():
    try:
        # No other monster has this exact trait name in the roster
        monster = next(row for row in load_monster_source_2014() if row.id == "ghost")
        assert not verified_arena_inert_trait_2014(monster, "Ephemeral")
    except Exception:
        logger.exception("Ephemeral source isolation failed")
        raise
