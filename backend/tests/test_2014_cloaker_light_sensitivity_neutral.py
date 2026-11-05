from __future__ import annotations

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


def test_light_sensitivity_exact_source_is_arena_neutral() -> None:
    card = next(m for m in load_monster_source_2014() if m.id == "cloaker")
    before = card.model_dump_json()
    assert verified_arena_inert_trait_2014(card, "Light Sensitivity")
    assert "Light Sensitivity" not in unsupported_traits_2014(card)
    assert card.model_dump_json() == before


@pytest.mark.parametrize("mutation", [
    "While in sunlight",
    "has advantage on attack rolls",
    "grants bright light",
])
def test_light_sensitivity_fails_closed_on_source_mutation(mutation: str) -> None:
    card = next(m for m in load_monster_source_2014() if m.id == "cloaker")
    original = card.source_traits or ""
    mutated_text = original.replace(
        "While in bright light",
        mutation,
        1,
    )
    mutated = card.model_copy(update={"source_traits": mutated_text})
    assert not verified_arena_inert_trait_2014(mutated, "Light Sensitivity")
    assert "Light Sensitivity" in unsupported_traits_2014(mutated)


def test_light_sensitivity_isolated_to_cloaker() -> None:
    card = next(m for m in load_monster_source_2014() if m.id == "magmin")
    assert not verified_arena_inert_trait_2014(card, "Light Sensitivity")
