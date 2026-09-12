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

    paralyzing = (
        "<p><strong>Breath Weapons (Recharge 5–6).</strong> The dragon uses one of the following "
        "breath weapons.</p>"
        "<p><strong>Paralyzing Breath.</strong> The dragon exhales paralyzing gas in a 30-foot cone. "
        "Each creature in that area must succeed on a DC 18 Constitution saving throw or be paralyzed "
        "for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending "
        "the effect on itself on a success.</p>"
    )
    parsed = parse_save_actions(paralyzing, {"breath-weapons": 5})
    assert parsed == [{
        "id": "paralyzing-breath", "name": "Paralyzing Breath",
        "save_ability": "constitution", "dc": 18, "range_ft": 30,
        "area": {"shape": "cone", "origin": "self", "length_ft": 30},
        "failure_control_effect": {
            "condition_id": "paralyzed", "expiry_timing": "target_turn_end",
            "duration_rounds": 10, "repeat_save_ability": "constitution",
            "repeat_save_dc": 18, "repeat_save_timing": "target_turn_end",
        },
        "resource_id": "breath-weapons", "resource_cost": 1, "animation": "paralyzed",
    }]

    fear = (
        "<p><strong>Frightful Presence.</strong> Each creature of the dragon's choice that is within "
        "120 feet of the dragon and aware of it must succeed on a DC 19 Wisdom saving throw or become "
        "frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, "
        "ending the effect on itself on a success. If a creature's saving throw is successful or the effect "
        "ends for it, the creature is immune to the dragon's Frightful Presence for the next 24 hours.</p>"
    )
    parsed = parse_save_actions(fear, {})
    assert parsed == [{
        "id": "frightful-presence", "name": "Frightful Presence",
        "save_ability": "wisdom", "dc": 19, "range_ft": 120,
        "area": {"shape": "emanation", "origin": "self", "radius_ft": 120},
        "failure_control_effect": {
            "condition_id": "frightened", "expiry_timing": "target_turn_end",
            "duration_rounds": 10, "repeat_save_ability": "wisdom", "repeat_save_dc": 19,
            "repeat_save_timing": "target_turn_end", "source_effect_immunity_on_end": True,
        },
        "source_effect_immunity_on_success": True, "animation": "fear",
    }]
    print("2014 save/control/AoE parser regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
