"""Roper Reel is only positional displacement under the locked arena policy."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_informational_action_proofs_2014 import (
    verified_nonactionable_action_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def _roper():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        return next(card for card in cards if card.id == "roper")
    except Exception:
        logger.exception("Could not load pinned Roper source")
        raise


def test_reel_exact_printed_displacement_only_is_arena_inert():
    try:
        roper = _roper()
        assert "Reel" in roper.action_names
        printed = source_sections_2014(
            roper.source_actions, include_continuations=True,
        )["Reel"]
        assert printed == (
            "The roper pulls each creature grappled by it up to 25 feet "
            "straight toward it."
        )
        assert verified_nonactionable_action_2014(roper, "Reel")
        assert "source:extra-action" not in basic_blockers_2014(roper)
        # Reel alone must not silently certify Grappling Tendrils or other traits.
        assert "source:trait" in basic_blockers_2014(roper)
    except Exception:
        logger.exception("Roper exact printed Reel proof failed")
        raise


@pytest.mark.parametrize("old,new", [
    ("25 feet", "35 feet"),
    ("grappled by it", "visible to it"),
    ("toward it.", "toward it and takes 1d6 damage."),
    ("toward it.", "toward it and becomes prone."),
])
def test_reel_mutations_fail_closed(old, new):
    try:
        roper = _roper()
        assert old in (roper.source_actions or "")
        changed = roper.model_copy(update={
            "source_actions": roper.source_actions.replace(old, new),
        })
        assert not verified_nonactionable_action_2014(changed, "Reel")
        assert "source:extra-action" in basic_blockers_2014(changed)
    except Exception:
        logger.exception("Roper Reel mutation proof failed: %s", old)
        raise


def test_reel_renamed_card_keeps_source_semantics():
    try:
        roper = _roper()
        renamed = roper.model_copy(update={
            "id": "another-puller", "name": "Other Creature",
        })
        assert verified_nonactionable_action_2014(renamed, "Reel")
    except Exception:
        logger.exception("Roper Reel identity-independent proof failed")
        raise
