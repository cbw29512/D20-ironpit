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
from app.content.monster_save_source_audit_2014 import unsupported_source_actions_2014
from app.content.monster_multiattack_variants_2014 import (
    source_form_qualified_multiattack_labels_2014,
)

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


@pytest.mark.parametrize("monster_id", ("werewolf", "wereboar", "wererat", "weretiger"))
def test_form_qualified_multiattack_is_source_verified_and_supported(monster_id):
    try:
        monster = _monster(monster_id)
        original = monster.model_dump_json()
        labels = source_form_qualified_multiattack_labels_2014(monster)
        assert len(labels) == 1
        assert labels.isdisjoint(
            {name.casefold() for name in unsupported_source_actions_2014(monster)}
        )
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("%s qualified Multiattack proof failed", monster_id)
        raise


@pytest.mark.parametrize("monster_id", ("werewolf", "wereboar", "wererat", "weretiger"))
def test_modified_form_qualified_multiattack_heading_fails_closed(monster_id):
    try:
        monster = _monster(monster_id)
        old = next(name for name in monster.action_names if name.casefold().startswith("multiattack"))
        new = old.replace("Humanoid or Hybrid", "Dragon")
        altered = monster.model_copy(update={
            "action_names": [new if name == old else name for name in monster.action_names],
            "source_actions": monster.source_actions.replace(old, new),
        })
        assert not source_form_qualified_multiattack_labels_2014(altered)
        assert new in unsupported_source_actions_2014(altered)
        assert "source:extra-action" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("%s edited Multiattack heading must fail closed", monster_id)
        raise


def test_form_qualified_family_clears_only_proven_multiattack_obligation():
    """Three cards admit; Weretiger keeps its unrelated printed Pounce blocker."""
    try:
        assert {monster_id: basic_blockers_2014(_monster(monster_id)) for monster_id in (
            "werewolf", "wereboar", "wererat", "weretiger",
        )} == {
            "werewolf": (),
            "wereboar": (),
            "wererat": (),
            "weretiger": ("source:trait",),
        }
        assert unsupported_traits_2014(_monster("weretiger")) == (
            "Pounce (Tiger or Hybrid Form Only)",
        )
    except Exception:
        logger.exception("Qualified Multiattack must not clear unrelated obligations")
        raise
