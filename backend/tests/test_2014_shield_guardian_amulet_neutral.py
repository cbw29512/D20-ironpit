"""Shield Guardian 2014 amulet-dependent traits and reaction source proof.

No amulet system exists in the Pit, so Bound, Spell Storing and Shield
cannot change a combat outcome. Strict full-paragraph match. Any mutation
fails closed. Regeneration remains independently supported.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_arena_unavailable_reactions_2014 import arena_unavailable_reaction_names_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _guardian():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "shield-guardian")
    except Exception:
        logger.exception("Pinned Shield Guardian source unavailable")
        raise


def test_shield_guardian_amulet_traits_and_reaction_are_source_verified():
    try:
        monster = _guardian()
        original = monster.model_dump_json()
        assert verified_arena_inert_trait_2014(monster, "Bound")
        assert verified_arena_inert_trait_2014(monster, "Spell Storing")
        assert "Bound" not in unsupported_traits_2014(monster)
        assert "Spell Storing" not in unsupported_traits_2014(monster)
        assert "Shield" in arena_unavailable_reaction_names_2014(monster)
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Shield Guardian amulet-neutral regression")
        raise


@pytest.mark.parametrize("trait,old,new", [
    ("Bound", "half of any damage the wearer takes", "all damage the wearer takes"),
    ("Bound", "within 60 feet", "within 120 feet"),
    ("Spell Storing", "4th level or lower", "5th level or lower"),
    ("Spell Storing", "any previously stored spell is lost", "previously stored spell remains"),
])
def test_modified_amulet_traits_fail_closed(trait, old, new):
    try:
        monster = _guardian()
        assert old in (monster.source_traits or "")
        altered = monster.model_copy(update={
            "source_traits": monster.source_traits.replace(old, new),
        })
        assert not verified_arena_inert_trait_2014(altered, trait)
        assert trait in unsupported_traits_2014(altered)
        assert "source:trait" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("Shield Guardian source mutation must fail closed")
        raise


def test_modified_shield_reaction_fails_closed():
    try:
        monster = _guardian()
        old = "+2 bonus to the wearer's AC"
        new = "+4 bonus to the wearer's AC"
        assert old in (monster.source_reactions or "")
        altered = monster.model_copy(update={
            "source_reactions": monster.source_reactions.replace(old, new),
        })
        assert "Shield" not in arena_unavailable_reaction_names_2014(altered)
    except Exception:
        logger.exception("Shield reaction mutation must fail closed")
        raise
