from __future__ import annotations

from app.content.capability_registry import get_capability_definition


_SOURCE_AREA_MONSTERS = (
    "srd-ankheg",
    "srd-black-dragon-wyrmling",
    "srd-blue-dragon-wyrmling",
    "srd-green-dragon-wyrmling",
    "srd-hell-hound",
    "srd-red-dragon-wyrmling",
    "srd-white-dragon-wyrmling",
    "srd-winter-wolf",
)


def test_area_monster_batch_uses_source_derived_registry() -> None:
    for monster_id in _SOURCE_AREA_MONSTERS:
        definition = get_capability_definition(monster_id)
        assert definition.archetype == "source-certified monster", monster_id
        assert definition.save_actions, monster_id
        assert any(action.area is not None for action in definition.save_actions), monster_id
