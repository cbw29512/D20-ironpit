"""Lycanthrope 2014 Shapechanger action source proof as nonactionable.

The polymorph is an action; statistics are the same except AC or size.
Under locked Pit rules this cannot alter combat outcomes. Exact source match; mutation fails closed.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_informational_action_proofs_2014 import verified_nonactionable_action_2014
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
def test_lycanthrope_shapechanger_action_is_source_verified_nonactionable(monster_id):
    try:
        monster = _monster(monster_id)
        original = monster.model_dump_json()
        assert verified_nonactionable_action_2014(monster, "Shapechanger")
        # For Werewolf this is the only remaining blocker; others have independent ones.
        if monster_id == "werewolf":
            assert "source:extra-action" not in basic_blockers_2014(monster)
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("%s Shapechanger action source proof failed", monster_id)
        raise


@pytest.mark.parametrize("monster_id,old,new", [
    ("werewolf", "Its statistics, other than its AC, are the same in each form",
     "Its AC and damage increase in hybrid form"),
])
def test_modified_lycanthrope_shapechanger_action_fails_closed(monster_id, old, new):
    try:
        monster = _monster(monster_id)
        assert old in (monster.source_traits or "")
        altered = monster.model_copy(update={
            "source_traits": monster.source_traits.replace(old, new),
        })
        assert not verified_nonactionable_action_2014(altered, "Shapechanger")
    except Exception:
        logger.exception("%s Shapechanger action mutation must fail closed", monster_id)
        raise
