"""Approved 2014 metal-sensing and equipment-corrosion exclusions."""
from __future__ import annotations

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _rust_monster():
    return next(monster for monster in load_monster_source_2014()
                if monster.id == "rust-monster")


@pytest.mark.parametrize("trait", ["Iron Scent", "Rust Metal"])
def test_approved_trait_remains_on_immutable_source_but_has_no_combat_binding(trait):
    monster = _rust_monster()
    before = monster.model_dump_json()
    assert trait in monster.trait_names
    assert verified_arena_inert_trait_2014(monster, trait)
    assert trait not in unsupported_traits_2014(monster)
    assert monster.model_dump_json() == before
    # Antennae remains an independent unapproved combat action blocker.
    assert "source:extra-action" in basic_blockers_2014(monster)


@pytest.mark.parametrize("trait,clause", [
    ("Iron Scent", "ferrous metal within 30 feet"),
    ("Rust Metal", "nonmagical weapon made of metal"),
])
def test_exact_source_clause_is_required_for_neutral_classification(trait, clause):
    monster = _rust_monster()
    assert clause.casefold() in (monster.source_traits or "").casefold()
    altered = monster.model_copy(update={
        "source_traits": monster.source_traits.replace(clause, "unverified source clause"),
    })
    assert not verified_arena_inert_trait_2014(altered, trait)
    assert trait in unsupported_traits_2014(altered)


def test_missing_trait_is_never_implicitly_exempt():
    monster = _rust_monster()
    altered = monster.model_copy(update={"trait_names": []})
    assert not verified_arena_inert_trait_2014(altered, "Iron Scent")
    assert not verified_arena_inert_trait_2014(altered, "Rust Metal")
