from __future__ import annotations

import pytest

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_spell_slot_resources_2014 import monster_spell_slot_resources_2014


def _source(name: str):
    return next(monster for monster in load_monster_source_2014() if monster.name == name)


def test_all_2014_prepared_casters_reuse_generic_slot_resources() -> None:
    casters = [monster for monster in load_monster_source_2014() if monster.spellcasting]
    assert len(casters) == 13
    for monster in casters:
        before = monster.model_dump(mode="json")
        resources = monster_spell_slot_resources_2014(monster)
        counts = monster.spellcasting["slots"]
        assert {resource.id: resource.max_uses for resource in resources} == {
            f"spell-slot-{level}": amount for level, amount in counts.items()
        }
        assert monster.model_dump(mode="json") == before


def test_archmage_2014_uses_printed_slots_without_additional_resources() -> None:
    archmage = _source("Archmage")
    assert [
        (resource.id, resource.max_uses)
        for resource in monster_spell_slot_resources_2014(archmage)
    ] == [
        (f"spell-slot-{level}", uses)
        for level, uses in enumerate((4, 3, 3, 3, 3, 1, 1, 1, 1), start=1)
    ]


def test_monsters_without_prepared_spellcasting_get_no_slots() -> None:
    assert monster_spell_slot_resources_2014(_source("Commoner")) == []


@pytest.mark.parametrize(
    ("bad_field", "expected"),
    [
        ({"source_complete": False}, "incomplete"),
        ({"slots": {"0": 4}}, "out-of-range"),
        ({"slots": {"1": 0}}, "invalid level-1 slot count"),
        ({"slots": {"1": True}}, "invalid level-1 slot count"),
        ({"spells": [{"id": "fire-bolt", "level": 0}, {"id": "fire-bolt", "level": 1}]}, "twice"),
        ({"spells": [{"id": "unknown", "level": 10}]}, "invalid level"),
    ],
)
def test_invalid_spellcasting_source_fails_closed(bad_field: dict, expected: str) -> None:
    archmage = _source("Archmage")
    corrupt = {**archmage.spellcasting, **bad_field}
    specimen = archmage.model_copy(update={"spellcasting": corrupt})
    with pytest.raises(ValueError, match=expected):
        monster_spell_slot_resources_2014(specimen)


def test_slot_adapter_preserves_noncasters_and_maintains_spellcasting_blocker() -> None:
    from app.content.monster_basic_candidates_2014 import basic_blockers_2014
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014

    goblin = adapt_basic_monster_2014(_source("Goblin"))
    assert not any(item.id.startswith("spell-slot-") for item in goblin.resources)

    mage = _source("Mage")
    assert "mechanic:spellcasting" in basic_blockers_2014(mage)
    with pytest.raises(ValueError, match="mechanic:spellcasting"):
        adapt_basic_monster_2014(mage)
