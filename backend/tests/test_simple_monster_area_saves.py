from __future__ import annotations

from app.content.simple_monster_source_resources import attach_limited_use_resources
from app.content.simple_monster_source_saves import parse_simple_save_actions


def test_recharge_cone_damage_save_compiles_to_shared_area_resource() -> None:
    row = {
        "name": "Hell Hound",
        "actions": (
            "Bite. Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Piercing damage plus 3 (1d6) Fire damage. "
            "Fire Breath (Recharge 5-6). Dexterity Saving Throw: DC 12, each creature in a 15-foot Cone. "
            "Failure: 17 (5d6) Fire damage. Success: Half damage."
        ),
        "bonusActions": "",
        "reactions": "",
    }

    saves = parse_simple_save_actions(row)
    assert len(saves) == 1
    action = saves[0]
    assert action["name"] == "Fire Breath (Recharge 5-6)"
    assert action["save_ability"] == "dexterity"
    assert action["dc"] == 12
    assert action["area"] == {"shape": "cone", "size_ft": 15}
    assert action["damage"] == {"count": 5, "size": 6, "bonus": 0}
    assert action["damage_type"] == "fire"
    assert action["success_damage"] == "half"

    resources, fingerprints = attach_limited_use_resources(row, [], saves)
    assert fingerprints == ["actions:Fire Breath (Recharge 5-6)"]
    assert resources == [{
        "id": "srd-hell-hound-actions-fire-breath-uses",
        "name": "Fire Breath",
        "max_uses": 1,
        "recharge": {"minimum": 5, "maximum": 6, "die_size": 6},
    }]
    assert action["resource_id"] == resources[0]["id"]
    assert action["resource_cost"] == 1


def test_recharge_line_damage_save_preserves_printed_width() -> None:
    row = {
        "name": "Ankheg",
        "actions": (
            "Bite. Melee Attack Roll: +5, reach 5 ft. Hit: 10 (2d6 + 3) Slashing damage plus 3 (1d6) Acid damage. "
            "Acid Spray (Recharge 6). Dexterity Saving Throw: DC 12, each creature in a 30-foot-long, 5-foot-wide Line. "
            "Failure: 14 (4d6) Acid damage. Success: Half damage."
        ),
        "bonusActions": "",
        "reactions": "",
    }

    saves = parse_simple_save_actions(row)
    assert len(saves) == 1
    action = saves[0]
    assert action["name"] == "Acid Spray (Recharge 6)"
    assert action["range_ft"] == 30
    assert action["area"] == {"shape": "line", "size_ft": 30, "width_ft": 5}
    assert action["damage"] == {"count": 4, "size": 6, "bonus": 0}
    assert action["damage_type"] == "acid"
    assert action["success_damage"] == "half"

    resources, _ = attach_limited_use_resources(row, [], saves)
    assert resources[0]["recharge"] == {"minimum": 6, "maximum": 6, "die_size": 6}
    assert action["resource_id"] == "srd-ankheg-actions-acid-spray-uses"
