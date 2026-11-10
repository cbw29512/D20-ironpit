"""Verify water-only 2014 source semantics stay neutral without waiving Fire Form."""

from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_inert_trait_proofs_2014 import (
    verified_approved_inert_trait_2014,
)
from app.content.monster_basic_candidates_2014 import (
    basic_blockers_2014,
    unsupported_traits_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def _source_card():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        matching = [card for card in cards if "Water Susceptibility" in card.trait_names]
        assert len(matching) == 1, "New water-only cards require a separate source audit."
        return matching[0]
    except Exception:
        logger.exception("Failed to inspect 2014 water-only source family.")
        raise


def test_exact_printed_water_only_effect_is_inert_without_clearing_fire_form():
    try:
        card = _source_card()
        original = card.model_dump_json()
        text = source_sections_2014(
            card.source_traits, include_continuations=True,
        ).get("Water Susceptibility")
        assert text
        assert verified_approved_inert_trait_2014(card, "Water Susceptibility")
        assert "Water Susceptibility" not in unsupported_traits_2014(card)
        assert "Fire Form" in unsupported_traits_2014(card)
        assert "source:trait" in basic_blockers_2014(card)
        assert card.model_dump_json() == original, "Immutable source card changed."
        renamed = card.model_copy(update={"id": "synthetic-water-only", "name": "Unrelated"})
        assert verified_approved_inert_trait_2014(renamed, "Water Susceptibility")
    except Exception:
        logger.exception("2014 water-only trait proof failed.")
        raise


@pytest.mark.parametrize("needle", (
    "moves in water",
    "gallon of water",
    "1 cold damage",
))
def test_changed_water_only_source_fails_closed(needle: str):
    try:
        card = _source_card()
        assert needle in (card.source_traits or "")
        changed = card.model_copy(update={
            "source_traits": card.source_traits.replace(needle, "unapproved combat rider"),
        })
        assert not verified_approved_inert_trait_2014(changed, "Water Susceptibility")
        assert "Water Susceptibility" in unsupported_traits_2014(changed)
    except Exception:
        logger.exception("Water-only source mutation guard failed: %s", needle)
        raise


def test_missing_heading_and_unheaded_added_rider_fail_closed():
    try:
        card = _source_card()
        source = card.source_traits or ""
        heading = "<strong>Water Susceptibility.</strong>"
        assert heading in source
        changed_heading = card.model_copy(update={
            "source_traits": source.replace(heading, "<strong>Other Trait.</strong>"),
        })
        assert not verified_approved_inert_trait_2014(changed_heading, "Water Susceptibility")

        # Continuation paragraphs belong to the trait, never silently vanish.
        extra = card.model_copy(update={
            "source_traits": source + "<p>It also deals cold damage to adjacent foes.</p>",
        })
        assert not verified_approved_inert_trait_2014(extra, "Water Susceptibility")
        removed_name = card.model_copy(update={
            "trait_names": [x for x in card.trait_names if x != "Water Susceptibility"],
        })
        assert not verified_approved_inert_trait_2014(removed_name, "Water Susceptibility")
    except Exception:
        logger.exception("Water-only source heading/continuation guard failed.")
        raise
