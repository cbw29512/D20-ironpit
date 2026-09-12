from import_2014_save_actions import parse_save_actions


def main() -> int:
    cone = (
        "<p><strong>Fire Breath (Recharge 5–6).</strong> The dragon exhales fire in a 15-foot cone. "
        "Each creature in that area must make a DC 11 Dexterity saving throw, taking 22 (4d10) "
        "fire damage on a failed save, or half as much damage on a successful one.</p>"
    )
    parsed = parse_save_actions(cone, {"fire-breath": 5})
    assert parsed == [{
        "id": "fire-breath", "name": "Fire Breath", "save_ability": "dexterity", "dc": 11,
        "range_ft": 15, "area": {"shape": "cone", "origin": "self", "length_ft": 15},
        "damage_dice_count": 4, "damage_dice_size": 10, "damage_bonus": 0,
        "damage_type": "fire", "success_damage": "half", "resource_id": "fire-breath",
        "resource_cost": 1,
    }]

    line = (
        "<p><strong>Lightning Breath (Recharge 6).</strong> The dragon exhales lightning in a "
        "30-foot line that is 5 feet wide. Each creature in that line must make a DC 12 Dexterity "
        "saving throw, taking 22 (4d10) lightning damage on a failed save, or half as much damage "
        "on a successful one.</p>"
    )
    parsed = parse_save_actions(line, {"lightning-breath": 6})
    assert parsed[0]["area"] == {
        "shape": "line", "origin": "self", "length_ft": 30, "width_ft": 5,
    }
    assert parsed[0]["resource_id"] == "lightning-breath"

    shared = (
        "<p><strong>Breath Weapons (Recharge 5–6).</strong> The dragon uses one of the following "
        "breath weapons.</p>"
        "<p><strong>Fire Breath.</strong> The dragon exhales fire in a 60-foot cone. Each creature "
        "in that area must make a DC 21 Dexterity saving throw, taking 66 (12d10) fire damage on "
        "a failed save, or half as much damage on a successful one.</p>"
    )
    parsed = parse_save_actions(shared, {"breath-weapons": 5})
    assert parsed[0]["resource_id"] == "breath-weapons"
    assert parsed[0]["id"] == "fire-breath"
    print("2014 save/AoE parser regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
