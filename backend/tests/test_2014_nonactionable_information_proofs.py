"""Printed source evidence for arena-neutral 2014 information-only abilities."""

from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_CASES = (
    ("aboleth", "Probing Telepathy"),
    ("androsphinx", "Inscrutable"),
    ("gynosphinx", "Inscrutable"),
)


def _source(monster_id: str):
    try:
        return next(m for m in load_monster_source_2014() if m.id == monster_id)
    except Exception:
        logger.exception("2014 source not found for informational trait %s", monster_id)
        raise


@pytest.mark.parametrize("monster_id,trait", _CASES)
def test_complete_source_is_neutral_without_approximating_combat_effects(monster_id, trait):
    monster = _source(monster_id)
    before = monster.model_dump_json()
    assert trait in monster.trait_names
    assert trait in source_sections_2014(monster.source_traits)
    assert verified_arena_inert_trait_2014(monster, trait)
    assert trait not in unsupported_traits_2014(monster)
    assert basic_blockers_2014(monster), "Other independent monster abilities remain blocked"
    assert monster.model_dump_json() == before


@pytest.mark.parametrize("monster_id,trait,replaced", (
    ("aboleth", "Probing Telepathy", "greatest desires"),
    ("aboleth", "Probing Telepathy", "aboleth can see the creature"),
    ("androsphinx", "Inscrutable", "that it refuses"),
    ("androsphinx", "Inscrutable", "read its thoughts"),
    ("gynosphinx", "Inscrutable", "sense its emotions"),
    ("gynosphinx", "Inscrutable", "disadvantage"),
))
def test_changed_printed_semantics_fail_closed(monster_id, trait, replaced):
    monster = _source(monster_id)
    source = monster.source_traits or ""
    assert replaced in source.casefold()
    # Case-insensitive replacement retains the whole card except the proof obligation.
    start = source.casefold().index(replaced)
    altered_source = source[:start] + "unproved behavior" + source[start + len(replaced):]
    altered = monster.model_copy(update={"source_traits": altered_source})
    assert not verified_arena_inert_trait_2014(altered, trait)
    assert trait in unsupported_traits_2014(altered)
    assert "source:trait" in basic_blockers_2014(altered)


@pytest.mark.parametrize("monster_id,trait", _CASES)
def test_missing_printed_heading_or_declared_trait_is_not_accepted(monster_id, trait):
    monster = _source(monster_id)
    src = monster.source_traits or ""
    heading = f"<strong>{trait}.</strong>"
    assert heading in src
    changed_heading = monster.model_copy(update={"source_traits": src.replace(heading, "<strong>Other.</strong>")})
    assert not verified_arena_inert_trait_2014(changed_heading, trait)
    changed_name = monster.model_copy(update={"trait_names": [name for name in monster.trait_names if name != trait]})
    assert not verified_arena_inert_trait_2014(changed_name, trait)

@pytest.mark.parametrize("monster_id", ("androsphinx", "gynosphinx"))
def test_informational_proof_never_hides_unbound_spellcasting(monster_id):
    monster = _source(monster_id)
    assert verified_arena_inert_trait_2014(monster, "Inscrutable")
    assert "Spellcasting" in unsupported_traits_2014(monster)
    assert "source:trait" in basic_blockers_2014(monster)
