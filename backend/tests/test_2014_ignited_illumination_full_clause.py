"""Strict 327-card proof for the lighting-only 2014 trait."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_ignited_illumination_2014 import source_proves_ignited_illumination_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _magmin():
    return next(m for m in load_monster_source_2014() if m.id == "magmin")


def test_327_cards_have_one_full_light_only_source_match():
    try:
        roster = load_monster_source_2014()
        matches = [m.id for m in roster if source_proves_ignited_illumination_2014(m)]
        assert len(roster) == 327
        assert matches == ["magmin"]
        card = _magmin()
        original = card.model_dump_json()
        assert verified_arena_inert_trait_2014(card, "Ignited Illumination")
        assert "Ignited Illumination" not in unsupported_traits_2014(card)
        assert "source:trait" not in basic_blockers_2014(card)
        # Full Touch source proof and no-douse AI now admit Magmin.
        assert basic_blockers_2014(card) == ()
        assert card.model_dump_json() == original
        assert source_proves_ignited_illumination_2014(
            card.model_copy(update={"id": "renamed-homebrew", "name": "Renamed Light Creature"})
        )
    except Exception:
        logger.exception("2014 light-only roster proof failed.")
        raise


@pytest.mark.parametrize("old,new", [
    ("As a bonus action", "As a reaction"),
    ("set itself ablaze or extinguish its flames", "set itself ablaze and burn nearby foes"),
    ("10-foot radius", "20-foot radius"),
    ("dim light for an additional 10 feet", "dim light for an additional 30 feet"),
    ("10 feet.</p>", "10 feet. Targets must make a DC 14 save.</p>"),
])
def test_mutated_light_trait_never_classifies_as_neutral(old: str, new: str):
    card = _magmin()
    assert old in (card.source_traits or "")
    altered = card.model_copy(update={
        "source_traits": (card.source_traits or "").replace(old, new),
    })
    assert not source_proves_ignited_illumination_2014(altered)
    assert "Ignited Illumination" in unsupported_traits_2014(altered)
    assert "source:trait" in basic_blockers_2014(altered)


def test_unheaded_continuation_and_removed_heading_fail_closed():
    card = _magmin()
    source = card.source_traits or ""
    continuation = card.model_copy(update={
        "source_traits": source + "<p>Nearby targets also take 1 fire damage.</p>",
    })
    assert not source_proves_ignited_illumination_2014(continuation)
    assert "source:trait" in basic_blockers_2014(continuation)
    missing = card.model_copy(update={
        "trait_names": [name for name in card.trait_names if name != "Ignited Illumination"],
    })
    assert not source_proves_ignited_illumination_2014(missing)
