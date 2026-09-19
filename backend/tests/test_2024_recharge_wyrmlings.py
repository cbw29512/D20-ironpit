from __future__ import annotations

from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.monsters_recharge_wyrmlings import build_recharge_wyrmlings
from app.domain.catalog import CoverageStatus

_NAMES = [
    "Black Dragon Wyrmling",
    "Blue Dragon Wyrmling",
    "Green Dragon Wyrmling",
    "Red Dragon Wyrmling",
    "White Dragon Wyrmling",
]

_EXPECTED = {
    "Black Dragon Wyrmling": ("Acid Breath", "dexterity", 11, "line", 15, 5, 5, 8, "acid"),
    "Blue Dragon Wyrmling": ("Lightning Breath", "dexterity", 12, "line", 30, 5, 6, 6, "lightning"),
    "Green Dragon Wyrmling": ("Poison Breath", "constitution", 11, "cone", 15, None, 6, 6, "poison"),
    "Red Dragon Wyrmling": ("Fire Breath", "dexterity", 13, "cone", 15, None, 7, 6, "fire"),
    "White Dragon Wyrmling": ("Cold Breath", "constitution", 12, "cone", 15, None, 5, 8, "cold"),
}


def _runtime_by_name():
    return {
        monster.name: monster
        for monster in build_legacy_monster_templates()
        if monster.name in _NAMES
    }


def test_wyrmlings_match_source_and_recharge_contract() -> None:
    runtime = _runtime_by_name()
    source = {row["name"]: row for row in load_monster_rows() if row["name"] in _NAMES}

    assert set(runtime) == set(_NAMES)
    for name in _NAMES:
        monster = runtime[name]
        breath_name, ability, dc, shape, length, width, dice_count, dice_size, damage_type = _EXPECTED[name]

        assert audit_monster_source(monster, source[name]) == []
        assert monster.attack_action is not None
        assert len(monster.attack_action.slots) == 2
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
        assert breath.resource_id is not None
        assert monster.resources[0].id == breath.resource_id
        assert monster.resources[0].max_uses == 1
        assert monster.recharge_rules[0].resource_id == breath.resource_id
        assert monster.recharge_rules[0].minimum_roll == 5


def test_wyrmling_builders_remain_content_only_until_parent_recharge_contract() -> None:
    direct = {monster.name: monster for monster in build_recharge_wyrmlings()}
    assert set(direct) == set(_NAMES)
    for monster in direct.values():
        assert len(monster.saving_throw_actions) == 1
        assert len(monster.resources) == 1
        assert len(monster.recharge_rules) == 1


def test_wyrmlings_are_raw_ready_on_stacked_recharge_branch() -> None:
    cards = {card.name: card for card in build_monster_catalog() if card.name in _NAMES}
    assert set(cards) == set(_NAMES)
    for name, card in cards.items():
        assert card.coverage_status is CoverageStatus.RAW_READY, (name, card.blockers)
        assert card.runnable_template_id == f"srd-{name.lower().replace(' ', '-')}"
        assert card.blockers == []
