"""Source-verified arena-inert Change Shape for approved 2014 metallic dragons."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_change_shape_policy_2014 import approved_inert_change_shape_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_save_capabilities_2014 import unsupported_source_actions_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)

_DRAGONS = (
    "adult-bronze-dragon", "adult-gold-dragon", "adult-silver-dragon",
    "ancient-brass-dragon", "ancient-bronze-dragon", "ancient-copper-dragon",
    "ancient-gold-dragon", "ancient-silver-dragon",
)


def _source(monster_id):
    try:
        return next(monster for monster in load_monster_source_2014() if monster.id == monster_id)
    except Exception:
        logger.exception("Missing pinned 2014 source for %s", monster_id)
        raise


@pytest.mark.parametrize("monster_id", _DRAGONS)
def test_change_shape_remains_printed_and_only_approved_action_is_inert(monster_id):
    try:
        monster = _source(monster_id)
        original = monster.model_dump_json()
        assert "change shape" in {name.casefold() for name in unsupported_source_actions_2014(monster)}
        assert approved_inert_change_shape_2014(monster)
        assert basic_blockers_2014(monster) == ()
        # Classifier must not rewrite the immutable printed card or its actions.
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Source validation failed for %s", monster_id)
        raise


@pytest.mark.parametrize("monster_id", _DRAGONS)
def test_change_shape_fails_closed_without_exact_printed_source(monster_id):
    try:
        monster = _source(monster_id)
        source = monster.source_actions or ""
        assert "magically polymorphs" in source
        altered = monster.model_copy(update={
            "source_actions": source.replace("magically polymorphs", "magically disappears"),
        })
        assert not approved_inert_change_shape_2014(altered)
        assert "source:extra-action" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("Fail-closed test failed for %s", monster_id)
        raise


def test_change_shape_not_globally_disabled_for_other_source_creatures():
    try:
        deva = _source("deva")
        assert not approved_inert_change_shape_2014(deva)
        assert "source:extra-action" in basic_blockers_2014(deva)
    except Exception:
        logger.exception("Unapproved Change Shape exclusion regression")
        raise


def test_roster_includes_eight_existing_complete_dragon_profiles():
    try:
        roster = {monster.id for monster in build_basic_2014_monsters()}
        for source_id in _DRAGONS:
            assert "2014-" + source_id in roster
    except Exception:
        logger.exception("2014 metallic dragon source-roster regression")
        raise
