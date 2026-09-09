from __future__ import annotations

from app.content.monster_forced_movement_rider import forced_movement_specs


def test_combined_melee_ranged_forced_movement_expands_to_two_runtime_modes() -> None:
    actions = (
        "Harpoon. Melee or Ranged Attack Roll: +6, reach 5 ft. or range 20/60 ft. "
        "Hit: 11 (2d6 + 4) Piercing damage. If the target is a Large or smaller creature, "
        "the attacker pulls the target up to 15 feet straight toward itself."
    )
    specs = forced_movement_specs(actions)
    assert len(specs) == 2
    assert all(effect.direction == "pull" for effect, _ in specs)
    assert all(effect.max_distance_ft == 15 for effect, _ in specs)
    assert all(effect.distance_mode == "up_to" for effect, _ in specs)
    assert all(size.value == "large" for _, size in specs if size is not None)


def test_single_mode_attack_and_save_each_contribute_one_runtime_mode() -> None:
    melee = (
        "Ram. Melee Attack Roll: +4, reach 5 ft. Hit: 7 Bludgeoning damage, "
        "and the target is pushed up to 10 feet straight away from the attacker."
    )
    save = (
        "Strength Saving Throw: DC 15, one creature. Failure: The target is pushed "
        "10 feet straight away from the attacker."
    )
    assert len(forced_movement_specs(melee)) == 1
    assert len(forced_movement_specs(save)) == 1
