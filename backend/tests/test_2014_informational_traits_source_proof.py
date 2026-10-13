from __future__ import annotations

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


@pytest.mark.parametrize("monster_id,trait,source_clause", [
    ("banshee", "Detect Life", "general direction"),
    ("couatl", "Shielded Mind", "sense its emotions"),
])
def test_approved_informational_trait_preserves_source_and_other_blockers(
    monster_id: str, trait: str, source_clause: str,
) -> None:
    monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
    original = monster.model_dump_json()
    assert trait in monster.trait_names
    assert source_clause in (monster.source_traits or "")
    assert verified_arena_inert_trait_2014(monster, trait)
    assert trait not in unsupported_traits_2014(monster)
    assert basic_blockers_2014(monster)  # Independent combat blockers remain.
    assert monster.model_dump_json() == original


@pytest.mark.parametrize("monster_id,trait,source_clause", [
    ("banshee", "Detect Life", "general direction"),
    ("couatl", "Shielded Mind", "sense its emotions"),
])
def test_approved_informational_trait_fails_closed_without_source_proof(
    monster_id: str, trait: str, source_clause: str,
) -> None:
    monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
    altered = monster.model_copy(update={
        "source_traits": (monster.source_traits or "").replace(source_clause, "missing proof"),
    })
    assert not verified_arena_inert_trait_2014(altered, trait)
    assert trait in unsupported_traits_2014(altered)


@pytest.mark.parametrize("monster_id,trait", [
    ("banshee", "Detect Life"),
    ("couatl", "Shielded Mind"),
])
def test_missing_printed_trait_never_gets_an_exemption(monster_id: str, trait: str) -> None:
    monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
    altered = monster.model_copy(update={
        "trait_names": [name for name in monster.trait_names if name != trait],
    })
    assert not verified_arena_inert_trait_2014(altered, trait)


def test_unapproved_sense_magic_stays_blocked() -> None:
    monster = next(m for m in load_monster_source_2014() if m.id == "chuul")
    assert not verified_arena_inert_trait_2014(monster, "Sense Magic")
    assert "Sense Magic" in unsupported_traits_2014(monster)
