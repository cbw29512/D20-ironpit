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
    assert parsed[0]["failure_control_effect"]["condition_id"] == "paralyzed"
    assert parsed[0]["resource_id"] == "breath-weapons"

    sleep = (
        "<p><strong>Breath Weapons (Recharge 5–6).</strong> The dragon uses one of the following "
        "breath weapons.</p>"
        "<p><strong>Sleep Breath.</strong> The dragon exhales sleep gas in a 30-foot cone. Each creature "
        "in that area must succeed on a DC 14 Constitution saving throw or fall unconscious for 1 minute. "
        "This effect ends for a creature if the creature takes damage or someone uses an action to wake it.</p>"
    )
    parsed = parse_save_actions(sleep, {"breath-weapons": 5})
    assert parsed == [{
        "id": "sleep-breath", "name": "Sleep Breath", "save_ability": "constitution", "dc": 14,
        "range_ft": 30, "area": {"shape": "cone", "origin": "self", "length_ft": 30},
        "failure_control_effect": {
            "condition_id": "unconscious", "expiry_timing": "source_turn_start",
            "duration_rounds": 10, "allowed_removal_action_ids": ["wake-sleeper"],
            "ends_on_damage": True,
        },
        "resource_id": "breath-weapons", "resource_cost": 1, "animation": "unconscious",
    }]

    fear = (
        "<p><strong>Frightful Presence.</strong> Each creature of the dragon's choice that is within "
        "120 feet of the dragon and aware of it must succeed on a DC 19 Wisdom saving throw or become "
        "frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, "
        "ending the effect on itself on a success. If a creature's saving throw is successful or the effect "
        "ends for it, the creature is immune to the dragon's Frightful Presence for the next 24 hours.</p>"
    )
    parsed = parse_save_actions(fear, {})
    assert parsed[0]["failure_control_effect"]["condition_id"] == "frightened"
    assert parsed[0]["source_effect_immunity_on_success"] is True
    print("2014 save/control/AoE parser regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
