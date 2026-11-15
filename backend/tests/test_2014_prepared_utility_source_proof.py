"""Positive, negative and source-mutation coverage for prepared utility spells."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_prepared_utility_source_2014 import (
    source_proven_prepared_utility_spells_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)

DETECT_CASTERS = frozenset({
    "Androsphinx", "Archmage", "Gynosphinx", "Lich", "Mage", "Spirit Naga",
})
HAND_CASTERS = frozenset({
    "Archmage", "Flameskull", "Gynosphinx", "Lich", "Mage", "Spirit Naga",
})


def _card(name: str):
    try:
        return next(card for card in load_monster_source_2014() if card.name == name)
    except Exception:
        logger.exception("2014 source monster %s missing", name)
        raise


@pytest.mark.parametrize("spell_id,casters", [
    ("detect-magic", DETECT_CASTERS),
    ("mage-hand", HAND_CASTERS),
])
def test_all_affected_casters_have_immutable_source_proof(spell_id, casters):
    try:
        for name in sorted(casters):
            card = _card(name)
            snapshot = card.model_dump_json()
            assert spell_id in source_proven_prepared_utility_spells_2014(card)
            assert card.model_dump_json() == snapshot
    except Exception:
        logger.exception("Positive utility spell family source proof failed")
        raise


@pytest.mark.parametrize("name,spell_id,other_spell", [
    ("Androsphinx", "detect-magic", "mage-hand"),
    ("Flameskull", "mage-hand", "detect-magic"),
])
def test_absent_spells_are_not_automatically_certified(name, spell_id, other_spell):
    try:
        proven = source_proven_prepared_utility_spells_2014(_card(name))
        assert spell_id in proven
        assert other_spell not in proven
    except Exception:
        logger.exception("Unprinted utility spell was admitted")
        raise


@pytest.mark.parametrize("mutation", ["wrong-level", "wrong-name", "extra-effect", "duplicate"])
def test_structured_source_mutations_fail_closed(mutation):
    try:
        card = _card("Mage")
        source = dict(card.spellcasting)
        spells = [dict(entry) for entry in source["spells"]]
        target = next(entry for entry in spells if entry["id"] == "detect-magic")
        if mutation == "wrong-level":
            target["level"] = 4
        elif mutation == "wrong-name":
            target["name"] = "detect thoughts"
        elif mutation == "extra-effect":
            target["damage"] = "5d6"
        else:
            spells.append(dict(target))
        source["spells"] = spells
        altered = card.model_copy(update={"spellcasting": source})
        assert not source_proven_prepared_utility_spells_2014(altered)
    except Exception:
        logger.exception("Altered utility spell source bypassed source proof")
        raise


@pytest.mark.parametrize("mutation", ["trait", "heading", "body", "complete"])
def test_absent_printed_source_or_incomplete_metadata_fails_closed(mutation):
    try:
        card = _card("Mage")
        if mutation == "trait":
            card = card.model_copy(update={
                "trait_names": [item for item in card.trait_names if item != "Spellcasting"],
            })
        elif mutation == "complete":
            data = dict(card.spellcasting)
            data["source_complete"] = False
            card = card.model_copy(update={"spellcasting": data})
        elif mutation == "heading":
            card = card.model_copy(update={
                "source_traits": (card.source_traits or "").replace(
                    "<strong>Spellcasting.</strong>", "<strong>Missing.</strong>",
                ),
            })
        else:
            card = card.model_copy(update={
                "source_traits": (card.source_traits or "").replace(
                    "detect magic", "detect future",
                ).replace("mage hand", "mage foot"),
            })
        assert not source_proven_prepared_utility_spells_2014(card)
    except Exception:
        logger.exception("Missing source proof was incorrectly accepted")
        raise



def test_flameskull_spell_list_must_be_immediately_adjacent():
    try:
        card = _card("Flameskull")
        assert "mage-hand" in source_proven_prepared_utility_spells_2014(card)
        source = card.source_traits or ""
        assert "<ul>" in source and "</ul>" in source
        altered = card.model_copy(update={
            "source_traits": source.replace(
                "</p><ul>", "</p><p>Unrelated intervening text.</p><ul>",
            ),
        })
        assert altered.source_traits != source
        assert "mage-hand" not in source_proven_prepared_utility_spells_2014(altered)
    except Exception:
        logger.exception("Nonadjacent HTML spell list passed source proof")
        raise
