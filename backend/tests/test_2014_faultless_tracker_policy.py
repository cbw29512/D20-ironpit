from __future__ import annotations

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _stalker():
    return next(item for item in load_monster_source_2014() if item.id == "invisible-stalker")


def test_faultless_tracker_is_source_retained_but_arena_inert() -> None:
    monster = _stalker()
    before = monster.model_dump_json()
    assert monster.trait_names == ["Invisibility", "Faultless Tracker"]
    assert verified_arena_inert_trait_2014(monster, "Faultless Tracker")
    assert not verified_arena_inert_trait_2014(monster, "Invisibility")
    assert unsupported_traits_2014(monster) == ("Invisibility",)
    assert basic_blockers_2014(monster) == ("source:trait",)
    with pytest.raises(ValueError, match="source:trait"):
        adapt_basic_monster_2014(monster)
    assert monster.model_dump_json() == before


@pytest.mark.parametrize("old,new", [
    ("given a quarry by its summoner", "gets a combat target"),
    ("knows the direction and distance to its quarry", "sees its target automatically"),
    ("same plane of existence", "any plane of existence"),
    ("knows the location of its summoner", "gains attack advantage near its summoner"),
])
def test_changed_tracking_effect_cannot_be_silently_excluded(old: str, new: str) -> None:
    source = _stalker()
    assert old in (source.source_traits or "")
    altered = source.model_copy(update={"source_traits": source.source_traits.replace(old, new)})
    assert not verified_arena_inert_trait_2014(altered, "Faultless Tracker")
    assert "Faultless Tracker" in unsupported_traits_2014(altered)
    assert basic_blockers_2014(altered) == ("source:trait",)


def test_absent_source_and_name_stay_fail_closed() -> None:
    original = _stalker()
    for altered in (
        original.model_copy(update={"source_traits": None}),
        original.model_copy(update={"trait_names": ["Invisibility"]}),
    ):
        assert not verified_arena_inert_trait_2014(altered, "Faultless Tracker")
    assert not verified_arena_inert_trait_2014(original, "Invisibility")
