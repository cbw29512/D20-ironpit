"""Prove printed 2014 Counterspell without granting unsupported reactions."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_counterspell_source_2014 import (
    source_proves_prepared_counterspell_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _source_casters():
    try:
        return [
            card for card in load_monster_source_2014()
            if isinstance(card.spellcasting, dict)
            and any(
                isinstance(item, dict) and item.get("id") == "counterspell"
                for item in card.spellcasting.get("spells", ())
            )
        ]
    except Exception:
        logger.exception("Cannot enumerate immutable Counterspell casters")
        raise


def test_all_source_counterspell_cards_are_proven_immutably():
    try:
        cards = _source_casters()
        assert len(cards) >= 3, "2014 prepared Counterspell cohort unexpectedly missing"
        for card in cards:
            snapshot = card.model_dump_json()
            assert source_proves_prepared_counterspell_2014(card), card.name
            assert card.model_dump_json() == snapshot
    except Exception:
        logger.exception("Prepared Counterspell source cohort proof failed")
        raise


@pytest.mark.parametrize("mutation", [
    "wrong-level", "wrong-name", "duplicate", "extra-parameter",
    "no-heading", "incomplete", "no-printed-spell",
])
def test_counterspell_source_mutations_fail_closed(mutation):
    try:
        card = _source_casters()[0]
        source = dict(card.spellcasting)
        spells = [dict(item) for item in source["spells"]]
        target = next(item for item in spells if item.get("id") == "counterspell")
        if mutation == "wrong-level":
            target["level"] = 2
        elif mutation == "wrong-name":
            target["name"] = "counter spell"
        elif mutation == "duplicate":
            spells.append(dict(target))
        elif mutation == "extra-parameter":
            target["bonus_action"] = True
        elif mutation == "incomplete":
            source["source_complete"] = False
        elif mutation == "no-heading":
            card = card.model_copy(update={
                "trait_names": [x for x in card.trait_names if x != "Spellcasting"],
            })
        elif mutation == "no-printed-spell":
            card = card.model_copy(update={
                "source_traits": (card.source_traits or "").replace(
                    "counterspell", "countershape",
                ),
            })
        source["spells"] = spells
        card = card.model_copy(update={"spellcasting": source})
        assert not source_proves_prepared_counterspell_2014(card), mutation
    except Exception:
        logger.exception("Counterspell source mutation was incorrectly accepted")
        raise


def test_non_caster_is_not_granted_counterspell():
    try:
        card = next(x for x in load_monster_source_2014() if x.name == "Commoner")
        assert not source_proves_prepared_counterspell_2014(card)
    except Exception:
        logger.exception("Non-caster incorrectly granted Counterspell")
        raise
