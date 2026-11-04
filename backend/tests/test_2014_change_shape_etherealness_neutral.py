"""Change Shape and Etherealness source proofs (locked Pit rules).

Night Hag / Oni Change Shape: stats identical except size (or none).
Ghost / Night Hag / Succubus Etherealness: plane shift with no cross-plane
effect possible under locked Pit rules. Exact source match; mutation fails closed.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_informational_action_proofs_2014 import verified_nonactionable_action_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _monster(monster_id: str):
    try:
        return next(row for row in load_monster_source_2014() if row.id == monster_id)
    except Exception:
        logger.exception("Pinned %s source unavailable", monster_id)
        raise


@pytest.mark.parametrize("monster_id,action", [
    ("night-hag", "Change Shape"),
    ("oni", "Change Shape"),
    ("ghost", "Etherealness"),
    ("night-hag", "Etherealness"),
    ("succubus-incubus", "Etherealness"),
])
def test_change_shape_etherealness_is_source_verified(monster_id, action):
    try:
        monster = _monster(monster_id)
        original = monster.model_dump_json()
        assert verified_nonactionable_action_2014(monster, action)
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("%s %s source proof failed", monster_id, action)
        raise


@pytest.mark.parametrize("monster_id,action,old,new", [
    ("night-hag", "Change Shape", "Her statistics are the same in each form",
     "Her AC and damage increase in humanoid form"),
    ("oni", "Change Shape", "Other than its size, its statistics are the same in each form",
     "Its size and attack bonus change"),
    ("ghost", "Etherealness", "it can't affect or be affected by anything on the other plane",
     "it can attack across planes"),
])
def test_modified_change_shape_etherealness_fails_closed(monster_id, action, old, new):
    try:
        monster = _monster(monster_id)
        assert old in (monster.source_actions or "")
        altered = monster.model_copy(update={
            "source_actions": monster.source_actions.replace(old, new),
        })
        assert not verified_nonactionable_action_2014(altered, action)
    except Exception:
        logger.exception("%s %s mutation must fail closed", monster_id, action)
        raise
