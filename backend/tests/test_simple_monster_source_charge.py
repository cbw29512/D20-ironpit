from app.content.simple_monster_source_attacks import parse_simple_attacks


def test_runup_bonus_damage_and_prone_are_attack_data_not_named_logic() -> None:
    row = {
        "name": "Unrelated Charger",
        "actions": (
            "Horn. Melee Attack Roll: +5, reach 5 ft. Hit: 9 (1d10 + 4) Piercing damage. "
            "If the target is a Large or smaller creature and the charger moved 25+ feet straight toward it "
            "immediately before the hit, the target takes an extra 7 (2d6) Piercing damage and has the Prone condition."
        ),
    }
    attacks, _ = parse_simple_attacks(row)
    charge = attacks[0]["charge"]
    assert charge == {
        "minimum_move_ft": 25,
        "max_target_size": "large",
        "bonus_damage": {"dice_count": 2, "dice_size": 6, "damage_bonus": 0, "damage_type": "piercing"},
        "prone_max_target_size": "large",
    }
    assert attacks[0]["effects"] == []


def test_runup_replacement_damage_is_generic_attack_data() -> None:
    row = {
        "name": "Unrelated Runner",
        "actions": (
            "Ram. Melee Attack Roll: +4, reach 5 ft. Hit: 9 (2d6 + 2) Bludgeoning damage, "
            "or 11 (2d8 + 2) Bludgeoning damage if the runner moved 20+ feet straight toward the target "
            "immediately before the hit."
        ),
    }
    attacks, _ = parse_simple_attacks(row)
    charge = attacks[0]["charge"]
    assert charge == {
        "minimum_move_ft": 20,
        "replacement_damage": {"dice_count": 2, "dice_size": 8, "damage_bonus": 2, "damage_type": "bludgeoning"},
    }
