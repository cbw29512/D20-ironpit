from app.content.canonical_combat_treasure import canonical_combat_treasure_history
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_treasure import (
    canonical_treasure_roll,
    resolve_combat_treasure,
    treasure_bonus,
)
from app.content.pregen_treasure_application import apply_combat_treasure_history


def test_treasure_power_uses_five_character_level_bands() -> None:
    expected = {
        2: 1, 4: 1,
        5: 2, 8: 2,
        9: 3, 12: 3,
        13: 4, 16: 4,
        17: 5, 20: 5,
    }
    for level, bonus in expected.items():
        assert treasure_bonus(level) == bonus


def test_single_d100_table_has_no_second_roll_and_100_guarantees_two_items() -> None:
    fighter = build_karnok_stoneward_level(2)

    assert resolve_combat_treasure(fighter, 2, 50) == []
    assert resolve_combat_treasure(fighter, 2, 51)[0].effect == "armor-class"
    assert resolve_combat_treasure(fighter, 2, 61)[0].effect == "weapon-enhancement"
    assert resolve_combat_treasure(fighter, 2, 71)[0].effect == "healing-potion"
    assert resolve_combat_treasure(fighter, 2, 81)[0].effect == "armor-class"
    assert resolve_combat_treasure(fighter, 2, 91)[0].slot == "accessory"

    jackpot = resolve_combat_treasure(fighter, 2, 100)
    assert len(jackpot) == 2
    assert {item.slot for item in jackpot} == {"offense", "defense"}


def test_magic_weapon_result_upgrades_the_characters_actual_primary_weapon() -> None:
    fighter = build_karnok_stoneward_level(5)
    award = resolve_combat_treasure(fighter, 5, 61)[0]

    assert award.target_id == fighter.weapon_attack.id
    assert fighter.weapon_attack.weapon.name in award.name
    assert award.bonus == 2

    upgraded = apply_combat_treasure_history(fighter, [award])
    assert upgraded.weapon_attack.attack_bonus == fighter.weapon_attack.attack_bonus + 2
    assert upgraded.weapon_attack.damage_bonus == fighter.weapon_attack.damage_bonus + 2


def test_magic_potion_is_a_real_one_use_combat_healing_action() -> None:
    fighter = build_karnok_stoneward_level(9)
    award = resolve_combat_treasure(fighter, 9, 71)[0]
    upgraded = apply_combat_treasure_history(fighter, [award])

    resource = next(item for item in upgraded.resources if item.id == "combat-healing-potion")
    action = next(item for item in upgraded.healing_actions if item.id == "combat-healing-potion")
    assert resource.max_uses == 1
    assert action.target_mode == "self"
    assert action.action_cost == "action"
    assert (action.dice_count, action.dice_size, action.healing_bonus) == (8, 4, 8)


def test_canonical_rolls_are_reproducible_and_history_persists_forward() -> None:
    first = canonical_treasure_roll("2024", "fighter", "champion", 7)
    second = canonical_treasure_roll("2024", "fighter", "champion", 7)
    assert first == second

    fighter = build_karnok_stoneward_level(12)
    history = canonical_combat_treasure_history(fighter, "fighter", "champion", 12)
    assert all(2 <= item.level <= 12 for item in history)
    assert all(item.roll == canonical_treasure_roll("2024", "fighter", "champion", item.level) for item in history)


def test_level_one_has_no_treasure_history_and_later_history_is_prefix_stable() -> None:
    fighter1 = build_karnok_stoneward_level(1)
    assert canonical_combat_treasure_history(fighter1, "fighter", "champion", 1) == []

    fighter8 = build_karnok_stoneward_level(8)
    fighter9 = build_karnok_stoneward_level(9)
    history8 = canonical_combat_treasure_history(fighter8, "fighter", "champion", 8)
    history9 = canonical_combat_treasure_history(fighter9, "fighter", "champion", 9)

    prefix9 = [item for item in history9 if item.level <= 8]
    assert [(item.level, item.roll, item.slot, item.effect) for item in prefix9] == [
        (item.level, item.roll, item.slot, item.effect) for item in history8
    ]
