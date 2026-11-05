"""Source-only arena-neutral proof for 2014 Gelatinous Cube Transparent.

Exact full-paragraph match. Any mutation fails closed and retains source:trait.
No name dispatch, no invented effects.
"""
import logging

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _source(monster_id="gelatinous-cube"):
    try:
        return next(row for row in load_monster_source_2014() if row.id == monster_id)
    except Exception:
        logger.exception("Missing pinned source for Transparent test: %s.", monster_id)
        raise


def test_exact_transparent_paragraph_is_arena_neutral():
    try:
        source = _source()
        original = source.model_dump_json()
        assert verified_arena_inert_trait_2014(source, "Transparent")
        assert "Transparent" not in unsupported_traits_2014(source)
        # Ooze Cube remains independently unbound
        assert "Ooze Cube" in unsupported_traits_2014(source)
        assert "source:trait" in basic_blockers_2014(source)
        assert source.model_dump_json() == original
    except Exception:
        logger.exception("Transparent exact-match classification changed immutable card.")
        raise


def test_mutated_transparent_fails_closed():
    try:
        source = _source()
        mutations = (
            ("DC 15", "DC 10"),
            ("Wisdom (Perception)", "Intelligence (Investigation)"),
            ("neither moved nor attacked", "moved or attacked"),
            ("surprised by the cube", "not surprised by the cube"),
            ("plain sight", "darkness"),
        )
        for before, after in mutations:
            changed = source.model_copy(update={"source_traits": source.source_traits.replace(before, after)})
            assert changed.source_traits != source.source_traits
            assert not verified_arena_inert_trait_2014(changed, "Transparent")
            assert "Transparent" in unsupported_traits_2014(changed)
            assert "source:trait" in basic_blockers_2014(changed)
    except Exception:
        logger.exception("Mutated Transparent incorrectly classified as neutral.")
        raise


def test_missing_heading_or_name_fails_closed():
    try:
        source = _source()
        no_heading = source.model_copy(update={"source_traits": source.source_traits.replace("<strong>Transparent.</strong>", "")})
        assert not verified_arena_inert_trait_2014(no_heading, "Transparent")
        no_name = source.model_copy(update={"trait_names": [n for n in source.trait_names if n != "Transparent"]})
        assert not verified_arena_inert_trait_2014(no_name, "Transparent")
    except Exception:
        logger.exception("Missing heading or trait name incorrectly admitted Transparent.")
        raise
