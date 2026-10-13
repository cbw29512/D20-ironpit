from __future__ import annotations

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014, basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014


@pytest.mark.parametrize("monster_id,trait", [
    ("banshee", "Detect Life"),
    ("chuul", "Sense Magic"),
    ("couatl", "Shielded Mind"),
])
def test_informational_trait_source_verified_and_not_a_combat_effect(monster_id, trait):
    monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
    original = monster.model_dump_json()
    assert trait in monster.trait_names
    assert verified_arena_inert_trait_2014(monster, trait)
    assert trait not in unsupported_traits_2014(monster)
    assert monster.model_dump_json() == original


@pytest.mark.parametrize("monster_id,trait,word", [
    ("banshee", "Detect Life", "general direction"),
    ("chuul", "Sense Magic", "120 feet"),
    ("couatl", "Shielded Mind", "sense its emotions"),
])
def test_source_proof_is_required_and_other_blockers_survive(monster_id, trait, word):
    monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
    assert monster.source_traits
    altered = monster.model_copy(update={
        "source_traits": monster.source_traits.replace(word, "arbitrary replacement"),
    })
    assert not verified_arena_inert_trait_2014(altered, trait)
    assert trait in unsupported_traits_2014(altered)
    assert basic_blockers_2014(monster)  # Other source attacks/actions remain unresolved.

@pytest.mark.parametrize("monster_id,trait", [
    ("banshee", "Detect Life"),
    ("chuul", "Sense Magic"),
    ("couatl", "Shielded Mind"),
])
def test_missing_printed_trait_never_receives_neutral_exemption(monster_id, trait):
    monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
    altered = monster.model_copy(update={
        "trait_names": [item for item in monster.trait_names if item != trait],
    })
    assert not verified_arena_inert_trait_2014(altered, trait)
