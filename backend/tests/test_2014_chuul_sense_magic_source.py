"""2014 Chuul's printed Sense Magic is informational, not a combat buff."""

from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def _chuul():
    try:
        return next(item for item in load_monster_source_2014() if item.id == "chuul")
    except Exception:
        logger.exception("Pinned 2014 Chuul source missing")
        raise


def test_sense_magic_source_proof_preserves_unchanged_card_and_other_blockers():
    try:
        monster = _chuul()
        original = monster.model_dump_json()
        assert "Sense Magic" in monster.trait_names
        assert "senses magic within 120 feet" in source_sections_2014(
            monster.source_traits
        )["Sense Magic"].casefold()
        assert verified_arena_inert_trait_2014(monster, "Sense Magic")
        assert "Sense Magic" not in unsupported_traits_2014(monster)
        # This informational classification must not certify unresolved attacks.
        assert basic_blockers_2014(monster)
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Chuul Sense Magic source proof failed")
        raise


@pytest.mark.parametrize("original,altered", [
    ("120 feet", "30 feet"),
    ("at will", "once a day"),
    ("detect magic", "detect evil"),
    ("itself magical", "itself extraordinary"),
])
def test_sense_magic_mutated_printed_behavior_fails_closed(original, altered):
    try:
        monster = _chuul()
        source = monster.source_traits or ""
        assert original in source
        modified = monster.model_copy(update={
            "source_traits": source.replace(original, altered),
        })
        assert not verified_arena_inert_trait_2014(modified, "Sense Magic")
        assert "Sense Magic" in unsupported_traits_2014(modified)
        assert "source:trait" in basic_blockers_2014(modified)
    except Exception:
        logger.exception("Mutated Chuul Sense Magic must fail closed")
        raise


def test_omitted_trait_cannot_be_auto_classified():
    try:
        monster = _chuul()
        modified = monster.model_copy(update={
            "trait_names": [name for name in monster.trait_names if name != "Sense Magic"],
        })
        assert not verified_arena_inert_trait_2014(modified, "Sense Magic")
    except Exception:
        logger.exception("Chuul Sense Magic provenance check failed")
        raise

def test_other_traits_cannot_prove_missing_sense_magic_paragraph():
    try:
        monster = _chuul()
        source = monster.source_traits or ""
        sections = source_sections_2014(source)
        assert "Sense Magic" in sections
        # Preserve the declared trait name, but remove the printed body.
        # A neighboring trait must never authorize Sense Magic by accident.
        altered = monster.model_copy(update={
            "source_traits": source.replace(
                "<strong>Sense Magic.</strong>",
                "<strong>Missing Source.</strong>",
            ),
        })
        assert not verified_arena_inert_trait_2014(altered, "Sense Magic")
        assert "Sense Magic" in unsupported_traits_2014(altered)
    except Exception:
        logger.exception("Chuul Sense Magic source isolation failed")
        raise
