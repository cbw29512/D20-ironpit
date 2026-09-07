from __future__ import annotations

from app.content.simple_monster_source_definitions import build_simple_source_definitions


_AREA_BATCH = {
    "Ankheg": ("line", 30, 5, "acid"),
    "Black Dragon Wyrmling": ("line", 15, 5, "acid"),
    "Blue Dragon Wyrmling": ("line", 30, 5, "lightning"),
    "Green Dragon Wyrmling": ("cone", 15, None, "poison"),
    "Hell Hound": ("cone", 15, None, "fire"),
    "Red Dragon Wyrmling": ("cone", 15, None, "fire"),
    "White Dragon Wyrmling": ("cone", 15, None, "cold"),
    "Winter Wolf": ("cone", 15, None, "cold"),
}


def test_simple_area_save_batch_is_fully_source_derived() -> None:
    definitions = build_simple_source_definitions()
    by_name = {definition.name: definition for definition in definitions.values()}

    assert _AREA_BATCH.keys() <= by_name.keys()
    for name, (shape, size_ft, width_ft, damage_type) in _AREA_BATCH.items():
        definition = by_name[name]
        area_actions = [action for action in definition.save_actions if action.area is not None]
        assert len(area_actions) == 1, name
        action = area_actions[0]
        assert action.area is not None
        assert action.area.shape == shape
        assert action.area.size_ft == size_ft
        assert action.area.width_ft == width_ft
        assert action.damage_type is not None
        assert action.damage_type.value == damage_type
        assert action.success_damage == "half"
        assert action.resource_id is not None
        assert action.resource_cost == 1
        resources = {resource.id: resource for resource in definition.resources}
        assert action.resource_id in resources
        resource = resources[action.resource_id]
        assert resource.max_uses == 1
        assert resource.recharge is not None
        assert resource.recharge.die_size == 6
