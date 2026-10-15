from __future__ import annotations

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


def aboleth():
    return next(m for m in load_monster_source_2014() if m.id == "aboleth")


def test_underwater_mucous_cloud_is_source_verified_and_printed_text_retained() -> None:
    monster = aboleth()
    before = monster.model_dump_json()
    assert "Mucous Cloud" in monster.trait_names
    assert verified_arena_inert_trait_2014(monster, "Mucous Cloud")
    assert "Mucous Cloud" not in unsupported_traits_2014(monster)
    assert monster.model_dump_json() == before


def test_mucous_cloud_rejected_without_underwater_source_clause() -> None:
    monster = aboleth()
    source = monster.source_traits
    assert source is not None
    for changed in (
        source.replace("While underwater", "While on land"),
        source.replace("transformative mucus", "harmless mist"),
        source.replace("<strong>Mucous Cloud.</strong>", "<strong>Other Trait.</strong>"),
    ):
        altered = monster.model_copy(update={"source_traits": changed})
        assert not verified_arena_inert_trait_2014(altered, "Mucous Cloud")
        assert "Mucous Cloud" in unsupported_traits_2014(altered)


def test_mucous_cloud_and_probing_telepathy_each_require_their_own_source_proof() -> None:
    monster = aboleth()
    assert verified_arena_inert_trait_2014(monster, "Probing Telepathy")
    assert "Probing Telepathy" not in unsupported_traits_2014(monster)
    changed = monster.model_copy(update={
        "source_traits": (monster.source_traits or "").replace(
            "greatest desires", "combat statistics",
        ),
    })
    assert not verified_arena_inert_trait_2014(changed, "Probing Telepathy")
    assert "Probing Telepathy" in unsupported_traits_2014(changed)


def test_aboleth_remains_blocked_by_independent_combat_mechanics() -> None:
    monster = aboleth()
    blockers = basic_blockers_2014(monster)
    assert "source:trait" not in blockers  # Printed information traits are verified.
    assert "attack:incomplete" in blockers
    assert "source:legendary" in blockers
