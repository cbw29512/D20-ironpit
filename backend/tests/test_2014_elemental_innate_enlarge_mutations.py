"""Source mutations cannot silently enable Enlarge or admit the Efreeti."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_innate_ai_exclusions_2014 import source_proven_arena_ai_excluded_innate_spells_2014
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


def test_efreeti_source_admits_only_with_all_spells_disposed():
    try:
        card = _source()
        before = card.model_dump_json()
        # Major Image is still on the reference card, while the arena
        # AI declines its nondamaging illusion Action rather than fabricating
        # an illusion-belief combat resolver.
        assert "major-image" in {
            x["id"] for x in card.innate_spellcasting["spells"]
        }
        assert "major-image" in source_proven_arena_ai_excluded_innate_spells_2014(card)
        assert basic_blockers_2014(card) == ()
        adapted = adapt_basic_monster_2014(card)
        assert adapted.id == "2014-efreeti"
        assert card.model_dump_json() == before
        # Changed printed effects fail closed, even if structured rows remain.
        altered = card.model_copy(update={
            "source_traits": card.source_traits.replace(
                "major image, plane shift", "major image, fireball, plane shift"
            )
        })
        assert "mechanic:spellcasting" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("2014 Efreeti full source classification failed.")
        raise
