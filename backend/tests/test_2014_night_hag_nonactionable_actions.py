"""2014 noncombat action proofs: reusable exact-clause classification.

Change Shape on this source changes no useful Pit statistics; the printed
Claws remain Hag Form Only. Nightmare Haunting requires a sleeping target
on another plane and an hour of contact, none of which the Pit provides.
Neither classification creates a new combat resolver or erases source data.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_informational_action_proofs_2014 import (
    verified_nonactionable_action_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)

_ACTIONS = ("Change Shape", "Nightmare Haunting (1/Day)")


def _card(monster_id: str):
    try:
        return next(
            monster for monster in load_monster_source_2014()
            if monster.id == monster_id
        )
    except Exception:
        logger.exception("2014 monster source missing: %s", monster_id)
        raise


def test_both_inert_actions_remove_night_hag_extra_action_blocker():
    try:
        monster = _card("night-hag")
        original = monster.model_dump_json()
        assert all(action in monster.action_names for action in _ACTIONS)
        assert all(verified_nonactionable_action_2014(monster, a) for a in _ACTIONS)
        # The real Sleep cast is now separately certified in the shared
        # HP-pool spell suite; neither inert Action may mask its binding.
        from app.content.monster_hp_pool_spell_bindings_2014 import innate_hp_pool_spells_2014
        assert {action.id for action in innate_hp_pool_spells_2014(monster)} == {"sleep"}
        blockers = basic_blockers_2014(monster)
        assert "source:extra-action" not in blockers
        assert "mechanic:spellcasting" not in blockers
        assert blockers == (), "Night Hag must have no remaining source blockers"
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Night Hag noncombat Action verification failed.")
        raise


@pytest.mark.parametrize("action,old,new", [
    ("Change Shape", "Her statistics are the same in each form.",
     "Her statistics improve in humanoid form."),
    ("Nightmare Haunting (1/Day)", "at least 1 hour",
     "at least 1 round"),
])
def test_combat_relevant_mutation_restores_blocker(action, old, new):
    try:
        monster = _card("night-hag")
        assert old in (monster.source_actions or "")
        altered = monster.model_copy(update={
            "source_actions": monster.source_actions.replace(old, new),
        })
        assert not verified_nonactionable_action_2014(altered, action)
        assert "source:extra-action" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("Fail-closed source mutation test failed for %s.", action)
        raise


@pytest.mark.parametrize("action", _ACTIONS)
def test_missing_printed_heading_fails_closed(action):
    try:
        monster = _card("night-hag")
        heading = f"<strong>{action}.</strong>"
        assert heading in (monster.source_actions or "")
        broken = monster.model_copy(update={
            "source_actions": monster.source_actions.replace(
                heading, "<strong>Unknown Action.</strong>", 1,
            ),
        })
        assert not verified_nonactionable_action_2014(broken, action)
        assert "source:extra-action" in basic_blockers_2014(broken)
    except Exception:
        logger.exception("Missing printed Action heading did not fail closed: %s", action)
        raise


def test_hidden_continuation_rider_restores_action_blocker():
    try:
        monster = _card("night-hag")
        altered = monster.model_copy(update={
            "source_actions": (monster.source_actions or "")
            + "<p>The haunting immediately deals psychic damage in combat.</p>",
        })
        assert not verified_nonactionable_action_2014(
            altered, "Nightmare Haunting (1/Day)",
        )
        assert "source:extra-action" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("Noncombat continuation rider validation failed.")
        raise


def test_source_identity_and_other_shapechangers_fail_closed():
    try:
        monster = _card("night-hag")
        renamed = monster.model_copy(update={
            "id": "renamed-dreamwalker", "name": "Renamed Dreamwalker",
        })
        assert all(verified_nonactionable_action_2014(renamed, a) for a in _ACTIONS)
        oni = _card("oni")
        assert not verified_nonactionable_action_2014(oni, "Change Shape")
        # The Oni's source-specific changed weapon dice cannot be dismissed.
        assert "source:extra-action" in basic_blockers_2014(oni)
    except Exception:
        logger.exception("Source-neutral Action identity test failed.")
        raise


def test_whole_roster_only_matching_complete_actions_are_neutralized():
    try:
        monsters = load_monster_source_2014()
        assert len(monsters) == 327
        matched = {
            (monster.id, name)
            for monster in monsters for name in monster.action_names
            if name in _ACTIONS
            and verified_nonactionable_action_2014(monster, name)
        }
        assert matched == {
            ("night-hag", "Change Shape"),
            ("night-hag", "Nightmare Haunting (1/Day)"),
        }
    except Exception:
        logger.exception("327-card noncombat Action coverage failed.")
        raise
