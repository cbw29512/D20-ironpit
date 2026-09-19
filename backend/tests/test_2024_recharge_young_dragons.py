from __future__ import annotations

from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.monsters_recharge_young_dragons import build_recharge_young_dragons
from app.domain.catalog import CoverageStatus
from app.domain.size import CreatureSize

_NAMES = [
    "Young Black Dragon",
    "Young Blue Dragon",
    "Young Green Dragon",
    "Young Red Dragon",
    "Young White Dragon",
]

_EXPECTED = {
    "Young Black Dragon": ("Acid Breath", "dexterity", 14, "line", 30, 5, 14, 6, "acid"),
    "Young Blue Dragon": ("Lightning Breath", "dexterity", 16, "line", 60, 5, 10, 10, "lightning"),
    "Young Green Dragon": ("Poison Breath", "constitution", 14, "cone", 30, None, 12, 6, "poison"),
    "Young Red Dragon": ("Fire Breath", "dexterity", 17, "cone", 30, None, 16, 6, "fire"),
    "Young White Dragon": ("Cold Breath", "constitution", 15, "cone", 30, None, 9, 8, "cold"),
}

_EXPECTED_IMMUNITY = {
    "Young Black Dragon": "acid",
    "Young Blue Dragon": "lightning",
    "Young Green Dragon": "poison",
    "Young Red Dragon": "fire",
    "Young White Dragon": "cold",
}

_EXPECTED_MOVEMENT = {
    "Young Black Dragon": (40, 80, 0, 40, 0),
    "Young Blue Dragon": (40, 80, 0, 0, 20),
    "Young Green Dragon": (40, 80, 0, 40, 0),
    "Young Red Dragon": (40, 80, 40, 0, 0),
    "Young White Dragon": (40, 80, 0, 40, 20),
}


def _runtime_by_name():
    return {
        monster.name: monster
        for monster in build_legacy_monster_templates()
        if monster.name in _NAMES
    }


def test_young_dragons_match_source_and_recharge_contract() -> None:
    runtime = _runtime_by_name()
    source = {row["name"]: row for row in load_monster_rows() if row["name"] in _NAMES}

    assert set(runtime) == set(_NAMES)
    for name in _NAMES:
        monster = runtime[name]
        breath_name, ability, dc, shape, length, width, dice_count, dice_size, damage_type = _EXPECTED[name]

        assert monster.size is CreatureSize.LARGE
        modes = monster.movement_modes
        assert (modes.walk_ft, modes.fly_ft, modes.climb_ft, modes.swim_ft, modes.burrow_ft) == _EXPECTED_MOVEMENT[name]
        assert audit_monster_source(monster, source[name]) == []
        assert monster.weapon_attack.weapon.name == "Rend"
        assert monster.weapon_attack.weapon.reach_ft == 10
        assert monster.attack_action is not None
        assert len(monster.attack_action.slots) == 3
        assert all(slot.attack_ids == [monster.weapon_attack.id] for slot in monster.attack_action.slots)

        breath = monster.saving_throw_actions[0]
        assert (breath.name, breath.save_ability, breath.dc) == (breath_name, ability, dc)
        assert breath.area is not None
        assert (breath.area.shape, breath.area.length_ft, breath.area.width_ft) == (shape, length, width)
        assert (breath.damage_dice_count, breath.damage_dice_size, breath.damage_type) == (
            dice_count,
            dice_size,
            damage_type,
        )
        assert breath.success_damage == "half"
        assert [item.value for item in monster.damage_immunities] == [_EXPECTED_IMMUNITY[name]]
        assert breath.resource_id is not None
        assert monster.resources[0].id == breath.resource_id
        assert monster.resources[0].max_uses == 1
        assert monster.recharge_rules[0].resource_id == breath.resource_id
        assert monster.recharge_rules[0].minimum_roll == 5


def test_young_dragon_builders_are_recharge_content_only() -> None:
    direct = {monster.name: monster for monster in build_recharge_young_dragons()}
    assert set(direct) == set(_NAMES)
    for monster in direct.values():
        assert len(monster.saving_throw_actions) == 1
        assert len(monster.resources) == 1
        assert len(monster.recharge_rules) == 1


def test_young_dragons_are_raw_ready_on_stacked_recharge_branch() -> None:
    cards = {card.name: card for card in build_monster_catalog() if card.name in _NAMES}
    assert set(cards) == set(_NAMES)
    for name, card in cards.items():
        assert card.coverage_status is CoverageStatus.RAW_READY, (name, card.blockers)
        assert card.runnable_template_id == f"srd-{name.lower().replace(' ', '-')}"
        assert card.blockers == []
