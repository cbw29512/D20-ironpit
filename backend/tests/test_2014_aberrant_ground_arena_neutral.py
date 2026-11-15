"""2014 Aberrant Ground is movement-only in the formation-only arena."""

from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def _mouther():
    try:
        # Read immutable SRD source rather than recreating a card with assumed stats.
        return next(card for card in load_monster_source_2014() if card.id == "gibbering-mouther")
    except Exception:
        logger.exception("Pinned 2014 Gibbering Mouther source missing")
        raise


def test_aberrant_ground_movement_only_clause_is_inert_but_not_other_traits():
    try:
        card = _mouther()
        original = card.model_dump_json()
        paragraphs = source_sections_2014(card.source_traits, include_continuations=True)
        assert "Aberrant Ground" in card.trait_names
        assert "Gibbering" in card.trait_names
        assert "reduced to 0" in paragraphs["Aberrant Ground"]
        assert verified_arena_inert_trait_2014(card, "Aberrant Ground")
        assert "Aberrant Ground" not in unsupported_traits_2014(card)
        # Do not waive Gibbering's reaction/action-disrupting Wisdom save.
        assert "Gibbering" in unsupported_traits_2014(card)
        assert "source:trait" in basic_blockers_2014(card)
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("2014 Aberrant Ground source / independent blockers failed")
        raise


@pytest.mark.parametrize("original,changed", [
    ("10-foot radius", "30-foot radius"),
    ("doughlike difficult terrain", "damaging difficult terrain"),
    ("DC 10 Strength", "DC 15 Strength"),
    ("speed reduced to 0", "hit points reduced to 0"),
    ("until the start of its next turn", "until the end of its next turn"),
])
def test_outcome_changing_source_mutations_fail_closed(original, changed):
    try:
        card = _mouther()
        source = card.source_traits or ""
        assert original in source
        changed_card = card.model_copy(update={
            "source_traits": source.replace(original, changed),
        })
        assert not verified_arena_inert_trait_2014(changed_card, "Aberrant Ground")
        assert "Aberrant Ground" in unsupported_traits_2014(changed_card)
        assert "source:trait" in basic_blockers_2014(changed_card)
    except Exception:
        logger.exception("Aberrant Ground mutation was not safely rejected")
        raise


def test_missing_source_or_trait_name_is_not_admitted():
    try:
        card = _mouther()
        missing_trait = card.model_copy(update={
            "trait_names": [name for name in card.trait_names if name != "Aberrant Ground"],
        })
        assert not verified_arena_inert_trait_2014(missing_trait, "Aberrant Ground")
        missing_text = card.model_copy(update={
            "source_traits": (card.source_traits or "").replace(
                "<strong>Aberrant Ground.</strong>",
                "<strong>Missing Source.</strong>",
            ),
        })
        assert not verified_arena_inert_trait_2014(missing_text, "Aberrant Ground")
    except Exception:
        logger.exception("Aberrant Ground missing-source isolation failed")
        raise
