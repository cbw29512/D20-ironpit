from __future__ import annotations

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


@pytest.mark.parametrize("monster_id,trait", [
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


@pytest.mark.parametrize("monster_id,trait,clause", [
    ("fire-elemental", "Water Susceptibility", "gallon of water"),
    ("shadow", "Sunlight Weakness", "while in sunlight"),
])
def test_environment_exclusion_requires_actual_source_semantics(
    monster_id: str, trait: str, clause: str,
) -> None:
    import re

    monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
    source = monster.source_traits or ""
    damaged, replacements = re.subn(
        re.escape(clause), "missing environmental trigger", source,
        count=1, flags=re.IGNORECASE,
    )
    assert replacements == 1
    altered = monster.model_copy(update={"source_traits": damaged})
    assert not verified_arena_inert_trait_2014(altered, trait)
    assert trait in unsupported_traits_2014(altered)
