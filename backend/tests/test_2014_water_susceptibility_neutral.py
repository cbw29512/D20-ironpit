"""Exact source proof that 2014 Water Susceptibility is arena-neutral."""

from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def _fire_elemental():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "fire-elemental")
    except Exception:
        logger.exception("2014 Fire Elemental source missing")
        raise


def test_exact_water_susceptibility_is_arena_neutral():
    monster = _fire_elemental()
    before = monster.model_dump_json()
    assert "Water Susceptibility" in monster.trait_names
    assert "Water Susceptibility" in source_sections_2014(monster.source_traits)
    assert verified_arena_inert_trait_2014(monster, "Water Susceptibility")
    assert "Water Susceptibility" not in unsupported_traits_2014(monster)
    # Fire Form remains independently unbound.
    assert "Fire Form" in unsupported_traits_2014(monster)
    assert "source:trait" in basic_blockers_2014(monster)
    assert monster.model_dump_json() == before


@pytest.mark.parametrize("replaced", (
    "moves in water",
    "gallon of water",
    "1 cold damage",
))
def test_mutated_water_susceptibility_fails_closed(replaced):
    monster = _fire_elemental()
    source = monster.source_traits or ""
    assert replaced in source.casefold()
    start = source.casefold().index(replaced)
    altered_source = source[:start] + "unproved context" + source[start + len(replaced):]
    altered = monster.model_copy(update={"source_traits": altered_source})
    assert not verified_arena_inert_trait_2014(altered, "Water Susceptibility")
    assert "Water Susceptibility" in unsupported_traits_2014(altered)


def test_missing_heading_or_trait_name_fails():
    monster = _fire_elemental()
    src = monster.source_traits or ""
    heading = "<strong>Water Susceptibility.</strong>"
    assert heading in src
    changed_heading = monster.model_copy(update={"source_traits": src.replace(heading, "<strong>Other.</strong>")})
    assert not verified_arena_inert_trait_2014(changed_heading, "Water Susceptibility")
    changed_name = monster.model_copy(update={"trait_names": [n for n in monster.trait_names if n != "Water Susceptibility"]})
    assert not verified_arena_inert_trait_2014(changed_name, "Water Susceptibility")
