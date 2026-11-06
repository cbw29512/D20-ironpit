from __future__ import annotations

from app.content.monster_basic_candidates_2014 import (
    basic_blockers_2014,
    is_arena_neutral_monster_2014,
    unsupported_traits_2014,
)
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014


def _source(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def test_2014_frog_is_arena_neutral_not_missing_engine_work() -> None:
    frog = _source("frog")

    assert frog.attacks == []
    assert {"Amphibious", "Standing Leap"} <= set(frog.trait_names)
    assert unsupported_traits_2014(frog) == ()
    assert is_arena_neutral_monster_2014(frog) is True
    assert basic_blockers_2014(frog) == ("arena:neutral",)
    assert "2014-frog" not in {item.id for item in build_basic_2014_monsters()}


def test_2014_arena_neutral_source_scan_finds_only_frog() -> None:
    matches = {
        monster.id
        for monster in load_monster_source_2014()
        if is_arena_neutral_monster_2014(monster)
    }

    assert len(load_monster_source_2014()) == 327
    assert matches == {"frog"}


def test_2014_frog_arena_neutral_fails_closed_on_source_mutation() -> None:
    frog = _source("frog")
    mutated = frog.model_copy(
        update={
            "source_traits": (frog.source_traits or "").replace("10 feet", "15 feet"),
        }
    )

    assert is_arena_neutral_monster_2014(mutated) is False
    assert "arena:neutral" not in basic_blockers_2014(mutated)


def test_2014_frog_arena_neutral_fails_closed_on_added_action() -> None:
    frog = _source("frog")
    mutated = frog.model_copy(
        update={"action_names": ["Bite"]},
    )

    assert is_arena_neutral_monster_2014(mutated) is False
    assert "arena:neutral" not in basic_blockers_2014(mutated)


def test_2014_arena_neutral_source_proof_ignores_card_identity() -> None:
    frog = _source("frog")
    renamed = frog.model_copy(update={"id": "renamed-neutral-card", "name": "Renamed"})

    assert is_arena_neutral_monster_2014(renamed) is True


def test_stirge_attaches_instead_of_being_excluded_from_arena() -> None:
    stirge = _source("stirge")

    assert is_arena_neutral_monster_2014(stirge) is False
    assert basic_blockers_2014(stirge) == ()
    assert "2014-stirge" in {item.id for item in build_basic_2014_monsters()}
