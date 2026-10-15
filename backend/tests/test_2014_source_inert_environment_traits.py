from __future__ import annotations

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


@pytest.mark.parametrize("monster_id,trait", [
    ("aboleth", "Probing Telepathy"),
    ("fire-elemental", "Water Susceptibility"),
    ("shadow", "Sunlight Weakness"),
])
def test_source_proven_arena_inert_trait(monster_id: str, trait: str) -> None:
    monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
    original = monster.model_dump_json()
    assert trait in monster.trait_names
    assert verified_arena_inert_trait_2014(monster, trait)
    assert trait not in unsupported_traits_2014(monster)
    assert monster.model_dump_json() == original
    tampered = monster.model_copy(update={
        "source_traits": (monster.source_traits or "").replace(
            f"<strong>{trait}.</strong>", f"<strong>Missing {trait}.</strong>",
        ),
    })
    assert not verified_arena_inert_trait_2014(tampered, trait)


def test_removed_printed_trait_never_qualifies() -> None:
    monster = next(m for m in load_monster_source_2014() if m.id == "aboleth")
    altered = monster.model_copy(update={"trait_names": ["Amphibious", "Mucous Cloud"]})
    assert not verified_arena_inert_trait_2014(altered, "Probing Telepathy")
