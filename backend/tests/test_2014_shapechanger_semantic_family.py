"""Roster-wide source proof for arena-inert 2014 Shapechanger clauses."""
from __future__ import annotations

import pytest

from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_shapechanger_neutral_2014 import source_proven_arena_inert_shapechanger_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _source(monster_id: str):
    return next(row for row in load_monster_source_2014() if row.id == monster_id)


def test_2014_shapechanger_semantic_scan_accounts_for_all_cards() -> None:
    monsters = load_monster_source_2014()
    applicable = [row for row in monsters if "Shapechanger" in row.trait_names]
    wired = [row.id for row in applicable if source_proven_arena_inert_shapechanger_2014(row)]

    assert len(monsters) == 327
    assert len(applicable) == 11
    assert set(wired) == {
        "doppelganger", "imp", "mimic", "quasit", "succubus-incubus",
        "werebear", "wereboar", "wererat", "weretiger", "werewolf",
    }
    assert [row.id for row in applicable if row.id not in wired] == ["vampire"]


@pytest.mark.parametrize("monster_id", ("doppelganger", "mimic", "succubus-incubus"))
def test_new_shapechanger_consumers_are_source_proven(monster_id: str) -> None:
    monster = _source(monster_id)
    original = monster.model_dump_json()

    assert source_proven_arena_inert_shapechanger_2014(monster)
    assert "Shapechanger" not in unsupported_traits_2014(monster)
    assert monster.model_dump_json() == original


def test_shapechanger_source_proof_is_identity_independent() -> None:
    monster = _source("doppelganger")
    renamed = monster.model_copy(update={
        "id": "renamed-card",
        "name": "Renamed",
        "source_traits": (monster.source_traits or "").replace(
            "The doppelganger can use its action",
            "The changeling can use its action",
        ),
    })

    assert source_proven_arena_inert_shapechanger_2014(renamed)


@pytest.mark.parametrize("monster_id", ("doppelganger", "mimic", "succubus-incubus"))
def test_shapechanger_source_mutation_fails_closed(monster_id: str) -> None:
    monster = _source(monster_id)
    mutated = monster.model_copy(update={
        "source_traits": (monster.source_traits or "").replace(
            "same in each form", "improved in each form",
        ),
    })

    assert not source_proven_arena_inert_shapechanger_2014(mutated)
    assert "Shapechanger" in unsupported_traits_2014(mutated)


def test_vampire_combat_active_shapechanger_remains_blocked() -> None:
    vampire = _source("vampire")

    assert not source_proven_arena_inert_shapechanger_2014(vampire)
    assert "Shapechanger" in unsupported_traits_2014(vampire)
