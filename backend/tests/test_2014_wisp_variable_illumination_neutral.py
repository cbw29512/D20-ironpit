from __future__ import annotations

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


def test_variable_illumination_exact_source_is_arena_neutral() -> None:
    card = next(m for m in load_monster_source_2014() if m.id == "will-o-wisp")
    before = card.model_dump_json()
    assert verified_arena_inert_trait_2014(card, "Variable Illumination")
    assert "Variable Illumination" not in unsupported_traits_2014(card)
    assert card.model_dump_json() == before


@pytest.mark.parametrize("mutation", [
    "sheds bright light in a 10- to 30-foot radius",
    "can alter the radius as a free action",
    "grants advantage on attack rolls",
])
def test_variable_illumination_fails_closed_on_source_mutation(mutation: str) -> None:
    card = next(m for m in load_monster_source_2014() if m.id == "will-o-wisp")
    original = card.source_traits or ""
    mutated_text = original.replace(
        "sheds bright light in a 5- to 20-foot radius",
        mutation,
        1,
    )
    mutated = card.model_copy(update={"source_traits": mutated_text})
    assert not verified_arena_inert_trait_2014(mutated, "Variable Illumination")
    assert "Variable Illumination" in unsupported_traits_2014(mutated)


def test_variable_illumination_isolated_to_will_o_wisp() -> None:
    card = next(m for m in load_monster_source_2014() if m.id == "magmin")
    assert not verified_arena_inert_trait_2014(card, "Variable Illumination")
