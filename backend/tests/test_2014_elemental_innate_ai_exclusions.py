"""2014 inert elemental innate choices must be fully source-proven, not name-cased."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_innate_ai_exclusions_2014 import (
    source_proven_arena_ai_excluded_innate_spells_2014,
)
from app.content.monster_innate_elemental_inert_2014 import (
    source_proven_elemental_inert_spells_2014,
)
from app.content.monster_innate_support_2014 import (
    innate_spell_names_2014, supports_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)

_EXPECTED = frozenset({"tongues", "conjure-elemental", "gaseous-form", "major-image"})


def _source():
    try:
        rows = load_monster_source_2014()
        assert len(rows) == 327
        return {row.id: row for row in rows}
    except Exception:
        logger.exception("2014 elemental innate source fixture failed.")
        raise


def test_full_source_scan_and_real_shared_classifier():
    try:
        cards = _source()
        matches = [card.id for card in cards.values()
                   if source_proven_elemental_inert_spells_2014(card)]
        assert matches == ["efreeti"]
        source = cards["efreeti"]
        before = source.model_dump_json()
        assert source_proven_elemental_inert_spells_2014(source) == _EXPECTED
        assert source_proven_arena_ai_excluded_innate_spells_2014(source) == _EXPECTED
        # Invisibility and Enlarge remain executable; only the approved
        # utility/illusion options are omitted by the automated AI.
        assert "invisibility" in {
            row.get("id") for row in source.innate_spellcasting["spells"]
        }
        assert "invisibility" in {
            spell.replace(" ", "-") for spell in innate_spell_names_2014(source)
        }
        assert supports_innate_spellcasting_2014(source)
        assert basic_blockers_2014(source) == ()
        assert source.model_dump_json() == before
    except Exception:
        logger.exception("2014 elemental source classification parity failed.")
        raise


@pytest.mark.parametrize("original, changed", [
    ("At will: detect magic", "At will: detect magic, fly"),
    ("3/day: enlarge/reduce, tongues", "3/day each: enlarge/reduce, tongues"),
    ("conjure elemental (fire elemental only)", "conjure elemental"),
    ("gaseous form, invisibility", "blur, invisibility"),
    ("major image, plane shift", "major image, fireball, plane shift"),
    ("spell save DC 15", "spell save DC 16"),
])
def test_unreviewed_printed_spell_changes_fail_closed(original, changed):
    try:
        card = _source()["efreeti"]
        assert original in card.source_traits
        altered = card.model_copy(update={
            "source_traits": card.source_traits.replace(original, changed),
        })
        assert not source_proven_elemental_inert_spells_2014(altered)
        assert not source_proven_arena_ai_excluded_innate_spells_2014(altered)
    except Exception:
        logger.exception("Mutated 2014 innate source was incorrectly accepted.")
        raise


@pytest.mark.parametrize("field, value", [
    ("uses_per_day", 2),
    ("shared_pool", False),
    ("qualifier", "water elemental only"),
    ("id", "dominate-person"),
])
def test_mutated_parsed_innate_row_fails_closed(field, value):
    try:
        card = _source()["efreeti"]
        spells = [dict(row) for row in card.innate_spellcasting["spells"]]
        index = 1 if field != "qualifier" else 3
        spells[index][field] = value
        changed = card.model_copy(update={
            "innate_spellcasting": {**card.innate_spellcasting, "spells": spells},
        })
        assert not source_proven_elemental_inert_spells_2014(changed)
        assert not source_proven_arena_ai_excluded_innate_spells_2014(changed)
    except Exception:
        logger.exception("2014 structured elemental spell mutation was accepted.")
        raise


def test_monster_identity_is_not_a_runtime_branch_and_other_spell_lists_survive():
    try:
        cards = _source()
        renamed = cards["efreeti"].model_copy(update={
            "id": "other-source-caster",
            "name": "Completely Renamed Creature",
        })
        assert source_proven_elemental_inert_spells_2014(renamed) == _EXPECTED
        assert source_proven_elemental_inert_spells_2014(cards["djinni"]) == frozenset()
        assert source_proven_arena_ai_excluded_innate_spells_2014(cards["djinni"]) == frozenset()
        # Cloud Giant's existing approved exclusions are unchanged by this
        # independent source-proven elemental package.
        assert source_proven_arena_ai_excluded_innate_spells_2014(
            cards["cloud-giant"]
        ) == frozenset({"fly", "telekinesis", "gaseous-form"})
    except Exception:
        logger.exception("Unrelated elemental/giant spell packages leaked exclusions.")
        raise
