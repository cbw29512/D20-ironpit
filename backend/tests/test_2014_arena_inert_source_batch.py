from __future__ import annotations

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


@pytest.mark.parametrize("monster_id,trait", [
    ("djinni", "Elemental Demise"),
    ("efreeti", "Elemental Demise"),
    ("planetar", "Divine Awareness"),
    ("solar", "Divine Awareness"),
    ("dryad", "Speak with Beasts and Plants"),
    ("dryad", "Tree Stride"),
    ("ghost", "Ethereal Sight"),
    ("homunculus", "Telepathic Bond"),
    ("otyugh", "Limited Telepathy"),
    ("pseudodragon", "Limited Telepathy"),
])
def test_source_proven_inert_trait_is_safe_without_changing_source(monster_id: str, trait: str) -> None:
    rows = load_monster_source_2014()
    monster = next((m for m in rows if m.id == monster_id), None)
    if monster is None:
        pytest.skip(f"No canonical source id {monster_id}")
    before = monster.model_dump_json()
    assert trait in monster.trait_names
    assert verified_arena_inert_trait_2014(monster, trait)
    assert trait not in unsupported_traits_2014(monster)
    altered = monster.model_copy(update={"source_traits": (monster.source_traits or "").replace(
        f"<strong>{trait}.</strong>", f"<strong>Missing {trait}.</strong>",
    )})
    assert not verified_arena_inert_trait_2014(altered, trait)
    assert monster.model_dump_json() == before
