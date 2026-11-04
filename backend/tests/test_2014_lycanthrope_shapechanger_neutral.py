"""Lycanthrope 2014 Shapechanger source proof and fail-closed guards.

Form change is an action; statistics are the same except AC or size.
Under locked Pit rules this cannot alter combat outcomes beyond the
already-printed card. Exact source match; mutation fails closed.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)

_IDS = ("werewolf", "werebear", "wererat", "wereboar", "weretiger")


def _monster(monster_id: str):
    try:
        return next(row for row in load_monster_source_2014() if row.id == monster_id)
    except Exception:
        logger.exception("Pinned %s source unavailable", monster_id)
        raise


@pytest.mark.parametrize("monster_id", _IDS)
def test_lycanthrope_shapechanger_is_source_verified(monster_id):
    try:
        monster = _monster(monster_id)
        original = monster.model_dump_json()
        assert verified_arena_inert_trait_2014(monster, "Shapechanger")
        assert "Shapechanger" not in unsupported_traits_2014(monster)
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("%s Shapechanger source proof failed", monster_id)
        raise


@pytest.mark.parametrize("monster_id,old,new", [
    ("werewolf", "Its statistics, other than its AC, are the same in each form",
     "Its AC and damage increase in hybrid form"),
    ("werebear", "Its statistics, other than its size and AC, are the same in each form",
     "Its size, AC and attack bonus change"),
    ("wererat", "Its statistics, other than its size, are the same in each form",
     "Its size and damage change"),
    ("wereboar", "Its statistics, other than its AC, are the same in each form",
     "Its AC and to-hit change"),
    ("weretiger", "Its statistics, other than its size, are the same in each form",
     "Its size and multiattack change"),
    ("werewolf", "It reverts to its true form if it dies.",
     "It keeps hybrid form if it dies."),
])
def test_modified_lycanthrope_shapechanger_fails_closed(monster_id, old, new):
    try:
        monster = _monster(monster_id)
        assert old in (monster.source_traits or "")
        altered = monster.model_copy(update={
            "source_traits": monster.source_traits.replace(old, new),
        })
        assert not verified_arena_inert_trait_2014(altered, "Shapechanger")
        assert "Shapechanger" in unsupported_traits_2014(altered)
        assert "source:trait" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("%s Shapechanger mutation must fail closed", monster_id)
        raise


def test_unrelated_shapechanger_does_not_inherit_lycanthrope_exception():
    try:
        monster = next(row for row in load_monster_source_2014() if row.id == "mimic")
        assert not verified_arena_inert_trait_2014(monster, "Shapechanger")
        assert "Shapechanger" in unsupported_traits_2014(monster)
    except Exception:
        logger.exception("Lycanthrope Shapechanger isolation failed")
        raise


@pytest.mark.parametrize("monster_id", ["werewolf", "wereboar", "wererat"])
def test_lycanthrope_form_qualified_multiattack_is_not_extra_action(monster_id):
    """Form-qualified Multiattack is the supported multiattack under locked Shapechanger policy.

    These three have no remaining multiattack:complex after policy reconciliation.
    """
    try:
        monster = _monster(monster_id)
        original = monster.model_dump_json()
        blockers = basic_blockers_2014(monster)
        assert "source:extra-action" not in blockers
        # For these three, this was the sole remaining blocker on current main.
        # Werewolf has none left; others may retain independent blockers if any.
        if monster_id == "werewolf":
            assert not blockers
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("%s form-qualified Multiattack classification failed", monster_id)
        raise
