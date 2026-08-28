from app.content.low_cr_monsters import build_bandit, build_guard
from app.content.test_roster import build_test_catalog
from app.domain.models import DuelMode, WeaponAttackKind
from app.main import app
from app.test_arena_api import create_mara_ambush, create_test_battle, get_test_roster


def test_bandit_matches_2024_basic_rules_combat_block() -> None:
    bandit = build_bandit()
    assert bandit.challenge_rating == "1/8"
    assert bandit.armor_class == 12
    assert bandit.max_hp == 11
    assert bandit.speed_ft == 30
    assert bandit.initiative_bonus == 1
    assert bandit.passive_perception == 10
    assert bandit.weapon_attack.attack_bonus == 3
    assert bandit.weapon_attack.weapon.name == "Scimitar"
    assert bandit.weapon_attack.weapon.dice_size == 6
    assert bandit.weapon_attack.ability_damage_modifier == 1
    crossbow = bandit.alternate_weapon_attacks[0]
    assert crossbow.attack_bonus == 3
    assert crossbow.weapon.name == "Light Crossbow"
    assert crossbow.weapon.dice_size == 8
    assert crossbow.weapon.normal_range_ft == 80
    assert crossbow.weapon.long_range_ft == 320


def test_guard_matches_2024_basic_rules_combat_block() -> None:
    guard = build_guard()
    assert guard.challenge_rating == "1/8"
    assert guard.armor_class == 16
    assert guard.max_hp == 11
    assert guard.speed_ft == 30
    assert guard.initiative_bonus == 1
    assert guard.passive_perception == 12
    assert guard.weapon_attack.weapon.name == "Spear"
    assert guard.weapon_attack.weapon.attack_kind is WeaponAttackKind.MELEE
    assert guard.weapon_attack.attack_bonus == 3
    thrown = guard.alternate_weapon_attacks[0]
    assert thrown.weapon.id == "spear"
    assert thrown.weapon.attack_kind is WeaponAttackKind.RANGED
    assert thrown.weapon.normal_range_ft == 20
    assert thrown.weapon.long_range_ft == 60
    assert thrown.attack_bonus == 3
    assert thrown.ability_damage_modifier == 1


def test_test_catalog_exposes_two_pregens_and_three_monsters() -> None:
    catalog = build_test_catalog()
    assert [item.id for item in catalog["characters"]] == [
        "aldric-vane-l1",
        "mara-vale-l1",
    ]
    assert [item.id for item in catalog["monsters"]] == [
        "srd-goblin-warrior",
        "srd-bandit",
        "srd-guard",
    ]


def test_selectable_routes_are_mounted() -> None:
    paths = {route.path for route in app.routes}
    assert "/api/test/roster" in paths
    assert "/api/test/battle/{character_id}/{monster_id}/{mode}" in paths
    assert "/api/test/ambush/{monster_id}" in paths


def test_selectable_roster_route_function_returns_catalog() -> None:
    catalog = get_test_roster()
    assert len(catalog["characters"]) == 2
    assert len(catalog["monsters"]) == 3


def test_selectable_melee_and_ranged_battles_run() -> None:
    melee = create_test_battle("mara-vale-l1", "srd-bandit", DuelMode.MELEE)
    ranged = create_test_battle("aldric-vane-l1", "srd-guard", DuelMode.RANGED)
    assert melee.fighter.template.id == "mara-vale-l1"
    assert melee.monster.template.id == "srd-bandit"
    assert ranged.fighter.template.id == "aldric-vane-l1"
    assert ranged.monster.template.id == "srd-guard"
    assert ranged.battlefield.starting_distance_ft == 20


def test_mara_ambush_accepts_any_test_monster() -> None:
    result = create_mara_ambush("srd-guard")
    assert result.fighter.template.id == "mara-vale-l1"
    assert result.monster.template.id == "srd-guard"
    assert result.battlefield.starting_distance_ft == 60
