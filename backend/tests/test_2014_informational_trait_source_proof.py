from __future__ import annotations

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


@pytest.mark.parametrize("monster_id,trait,clause", [
    ("banshee", "Detect Life", "general direction"),
    ("couatl", "Shielded Mind", "sense its emotions"),
])
def test_source_verified_information_is_inert_without_changing_printed_card(
    monster_id: str, trait: str, clause: str,
) -> None:
    card = next(m for m in load_monster_source_2014() if m.id == monster_id)
    before = card.model_dump_json()
    assert clause in (card.source_traits or "")
    assert verified_arena_inert_trait_2014(card, trait)
    assert trait not in unsupported_traits_2014(card)
    assert card.model_dump_json() == before


@pytest.mark.parametrize("monster_id,trait,clause", [
    ("banshee", "Detect Life", "general direction"),
    ("couatl", "Shielded Mind", "sense its emotions"),
])
def test_informational_exemption_fails_closed_on_source_mutation(
    monster_id: str, trait: str, clause: str,
) -> None:
    card = next(m for m in load_monster_source_2014() if m.id == monster_id)
    mutated = card.model_copy(update={
        "source_traits": (card.source_traits or "").replace(clause, "missing source proof"),
    })
    assert not verified_arena_inert_trait_2014(mutated, trait)
    assert trait in unsupported_traits_2014(mutated)


def test_other_informational_trait_requires_its_own_verified_source() -> None:
    card = next(m for m in load_monster_source_2014() if m.id == "chuul")
    assert not verified_arena_inert_trait_2014(card, "Sense Magic")
    assert "Sense Magic" in unsupported_traits_2014(card)
