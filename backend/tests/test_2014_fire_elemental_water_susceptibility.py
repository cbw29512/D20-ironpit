from __future__ import annotations

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


def fire_elemental():
    return next(m for m in load_monster_source_2014() if m.id == "fire-elemental")


def test_water_susceptibility_is_source_verified_arena_inert() -> None:
    monster = fire_elemental()
    before = monster.model_dump_json()
    assert "Water Susceptibility" in monster.trait_names
    assert verified_arena_inert_trait_2014(monster, "Water Susceptibility")
    assert "Water Susceptibility" not in unsupported_traits_2014(monster)
    assert monster.model_dump_json() == before


def test_water_susceptibility_rejected_without_water_source_clauses() -> None:
    monster = fire_elemental()
    source = monster.source_traits
    assert source is not None
    for changed in (
        source.replace("moves in water", "moves on land"),
        source.replace("gallon of water splashed", "gallon of oil splashed"),
        source.replace("<strong>Water Susceptibility.</strong>", "<strong>Other Trait.</strong>"),
    ):
        altered = monster.model_copy(update={"source_traits": changed})
        assert not verified_arena_inert_trait_2014(altered, "Water Susceptibility")
        assert "Water Susceptibility" in unsupported_traits_2014(altered)


def test_fire_elemental_still_blocked_by_fire_form() -> None:
    monster = fire_elemental()
    blockers = basic_blockers_2014(monster)
    assert "source:trait" in blockers  # Fire Form remains
    assert "Water Susceptibility" not in unsupported_traits_2014(monster)
    assert "Fire Form" in unsupported_traits_2014(monster)
