"""Strict source-neutral planar shift proof under the locked Pit planar ban."""
from __future__ import annotations

import logging

from app.content.monster_arena_action_policy_2014 import source_proven_ethereal_shift_action_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_informational_action_proofs_2014 import verified_nonactionable_action_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _card():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        return next(card for card in cards if card.id == "succubus-incubus")
    except Exception:
        logger.exception("Failed to load immutable 2014 planar-shift source")
        raise


def test_complete_planar_shift_uses_existing_locked_arena_ban():
    try:
        monster = _card()
        original = monster.model_dump_json()
        assert "Etherealness" in monster.action_names
        assert source_proven_ethereal_shift_action_2014(monster, "Etherealness")
        assert verified_nonactionable_action_2014(monster, "Etherealness")
        # The two printed combat actions still use their existing save/attack
        # capabilities. Only the purely out-of-plane Action is unavailable.
        assert basic_blockers_2014(monster) == ()
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("2014 planar-shift admission proof failed")
        raise


def test_planar_shift_source_identity_is_not_combat_dispatch():
    try:
        monster = _card().model_copy(update={
            "id": "different-fiend", "name": "Different Fiend",
        })
        assert source_proven_ethereal_shift_action_2014(monster, "Etherealness")
        assert verified_nonactionable_action_2014(monster, "Etherealness")
        assert basic_blockers_2014(monster) == ()
    except Exception:
        logger.exception("Source-neutral planar-shift proof failed")
        raise


def test_unknown_new_outcome_and_action_label_fail_closed():
    try:
        monster = _card()
        original = monster.source_actions or ""
        for old, new in (
            ("The fiend magically enters the Ethereal Plane from the Material Plane, or vice versa.",
             "The fiend magically enters the Ethereal Plane from the Material Plane, or vice versa. Each enemy takes 5 psychic damage."),
            ("Ethereal Plane", "Astral Plane"),
            ("or vice versa.", "or vice versa, stunning its enemies."),
        ):
            assert old in original
            mutated = monster.model_copy(update={
                "source_actions": original.replace(old, new),
            })
            assert not source_proven_ethereal_shift_action_2014(mutated, "Etherealness")
            assert not verified_nonactionable_action_2014(mutated, "Etherealness")
            assert "source:extra-action" in basic_blockers_2014(mutated)
        renamed = monster.model_copy(update={"action_names": [
            "Unproved Shift" if name == "Etherealness" else name
            for name in monster.action_names
        ]})
        assert not source_proven_ethereal_shift_action_2014(renamed, "Etherealness")
    except Exception:
        logger.exception("Planar-shift mutation proof failed")
        raise
