"""Source mutations cannot silently enable Enlarge or admit the Efreeti."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_innate_enlarge_2014 import source_proven_innate_enlarge_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(card for card in load_monster_source_2014()
                    if card.id == "efreeti")
    except Exception:
        logger.exception("2014 source card not found for Enlarge mutation tests.")
        raise


@pytest.mark.parametrize("changes", [
    {"source_traits": ("At will: detect magic", "At will: detect magic, fly")},
    {"source_traits": ("3/day: enlarge/reduce", "2/day: enlarge/reduce")},
    {"source_actions": ("2d6 + 6", "2d8 + 6")},
    {"size": ("Large", "Gargantuan")},
])
def test_mutations_fail_closed(changes):
    try:
        card = _source()
        updated = {}
        for key, (old, new) in changes.items():
            value = getattr(card, key)
            assert old in value
            updated[key] = value.replace(old, new)
        altered = card.model_copy(update=updated)
        assert source_proven_innate_enlarge_2014(altered) == []
    except Exception:
        logger.exception("Source mutation unexpectedly kept Enlarge available.")
        raise


def test_other_spells_still_block_entire_efreeti_admission():
    try:
        card = _source()
        assert "mechanic:spellcasting" in basic_blockers_2014(card)
        # No fabricated Major Image effects or premature monster admission.
        assert "major-image" in {
            x["id"] for x in card.innate_spellcasting["spells"]
        }
    except Exception:
        logger.exception("Efreeti admission was incorrectly forced.")
        raise
