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


def test_stirge_removal_remains_distinct_from_arena_neutral() -> None:
    stirge = _source("stirge")

    assert is_arena_neutral_monster_2014(stirge) is False
    assert basic_blockers_2014(stirge) == ("arena:removed",)
