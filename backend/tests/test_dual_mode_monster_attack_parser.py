from __future__ import annotations

from app.content.monster_simple_attack_parser import parse_simple_attacks


def test_dual_mode_attack_preserves_reach_range_and_forced_pull() -> None:
    row = {
        "name": "Dual Mode Test Creature",
        "actions": (
            "Harpoon. Melee or Ranged Attack Roll: +6, reach 5 ft. or range 20/60 ft. "
            "Hit: 11 (2d6 + 4) Piercing damage. If the target is a Large or smaller creature, "
            "the creature pulls the target up to 15 feet straight toward itself."
        ),
    }

    attacks = parse_simple_attacks(row)

    assert [attack.id for attack in attacks] == [
        "srd-dual-mode-test-creature-harpoon-melee",
        "srd-dual-mode-test-creature-harpoon-ranged",
    ]
    assert attacks[0].weapon.reach_ft == 5
    assert attacks[1].weapon.normal_range_ft == 20
    assert attacks[1].weapon.long_range_ft == 60
    for attack in attacks:
        assert attack.control_effect is not None
        assert attack.control_effect.forced_movement is not None
        assert attack.control_effect.forced_movement.direction == "pull"
        assert attack.control_effect.forced_movement.max_distance_ft == 15
        assert attack.control_effect.forced_movement.distance_mode == "up_to"
