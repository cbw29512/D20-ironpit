"""Read Thoughts carries only Pit-unavailable information/social checks."""
from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_informational_action_proofs_2014 import (
    verified_nonactionable_action_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def test_full_327_card_source_scan_has_exactly_one_read_thoughts() -> None:
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        applicable = [card for card in cards if "Read Thoughts" in card.action_names]
        assert len(applicable) == 1
        card = applicable[0]
        assert card.id == "doppelganger"
        assert verified_nonactionable_action_2014(card, "Read Thoughts")
        assert "source:extra-action" not in basic_blockers_2014(card)
        assert "source:trait" in basic_blockers_2014(card)
    except Exception:
        logger.exception("2014 source noncombat action verification failed.")
        raise


def test_exact_source_proof_rejects_any_new_combat_effect() -> None:
    try:
        card = next(x for x in load_monster_source_2014() if x.id == "doppelganger")
        before = card.model_dump_json()
        assert verified_nonactionable_action_2014(card, "Read Thoughts")
        altered = card.model_copy(update={
            "source_actions": card.source_actions.replace(
                "checks against the target.",
                "checks against the target. Its next attack has advantage.",
            )
        })
        assert not verified_nonactionable_action_2014(altered, "Read Thoughts")
        assert "source:extra-action" in basic_blockers_2014(altered)
        # Source labels/identities never choose runtime behavior.
        renamed = card.model_copy(update={
            "id": "homebrew-renamed", "name": "Renamed Thinker",
        })
        assert verified_nonactionable_action_2014(renamed, "Read Thoughts")
        assert not verified_nonactionable_action_2014(card, "Slam")
        assert card.model_dump_json() == before
    except Exception:
        logger.exception("2014 informational action source mutation test failed.")
        raise
