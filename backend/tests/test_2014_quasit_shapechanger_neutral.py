"""Quasit movement-only Shapechanger source proof regression tests."""
from __future__ import annotations

import logging
import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _quasit():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "quasit")
    except Exception:
        logger.exception("Pinned Quasit card unavailable")
        raise


def test_shapechanger_neutral_but_remaining_combat_actions_block():
    try:
        monster = _quasit()
        original = monster.model_dump_json()
        assert verified_arena_inert_trait_2014(monster, "Shapechanger")
        assert "Shapechanger" not in unsupported_traits_2014(monster)
        blockers = basic_blockers_2014(monster)
        assert "attack:complex" in blockers
        assert "source:extra-action" in blockers
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Quasit source proof failed")
        raise


@pytest.mark.parametrize("old,new", [
    ("Its statistics are the same in each form", "Its AC increases in beast form"),
    ("except for the speed changes noted", "except for damage and speed"),
    ("fly 40 ft.", "fly 80 ft."),
    ("swim 40 ft.", "swim 80 ft."),
    ("It reverts to its true form if it dies.", "It does not revert if it dies."),
])
def test_changed_shapechanger_source_fails_closed(old, new):
    try:
        monster = _quasit()
        assert old in monster.source_traits
        altered = monster.model_copy(update={"source_traits": monster.source_traits.replace(old, new)})
        assert not verified_arena_inert_trait_2014(altered, "Shapechanger")
        assert "Shapechanger" in unsupported_traits_2014(altered)
        assert "source:trait" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("Quasit Shapechanger mutation proof failed")
        raise


def test_other_shapechanger_not_classified():
    try:
        vampire = next(row for row in load_monster_source_2014() if row.id == "vampire")
        assert not verified_arena_inert_trait_2014(vampire, "Shapechanger")
    except Exception:
        logger.exception("Unrelated shapechanger was incorrectly admitted")
        raise
