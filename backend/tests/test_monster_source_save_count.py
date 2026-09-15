from app.content.monster_source_save_count import source_action_save_count


def test_counts_immediate_on_hit_save() -> None:
    actions = (
        "Bite. Melee Attack Roll: +4, reach 5 ft. Hit: 4 Piercing damage. "
        "If the target is a creature, it is subjected to the following effect. "
        "Constitution Saving Throw: DC 12. First Failure: The target has the Poisoned condition."
    )

    assert source_action_save_count(actions) == 1


def test_ignores_long_rest_triggered_save() -> None:
    actions = (
        "Bite. Melee Attack Roll: +6, reach 5 ft. Hit: 12 Piercing damage, and the target has the Poisoned condition. "
        "Whenever the Poisoned target finishes a Long Rest, it is subjected to the following effect. "
        "Constitution Saving Throw: DC 15. Failure: The target's Hit Point maximum decreases. "
        "Tentacle Slam. Constitution Saving Throw: DC 14, each creature Grappled by the otyugh."
    )

    assert source_action_save_count(actions) == 1


def test_ignores_repeat_save_in_same_action_lifecycle() -> None:
    actions = (
        "Paralyzing Tentacles. Constitution Saving Throw: DC 13, one creature. "
        "At the end of each of its turns, the target repeats the Constitution Saving Throw: DC 13."
    )

    assert source_action_save_count(actions) == 1


def test_counts_distinct_initial_action_saves() -> None:
    actions = (
        "First Effect. Dexterity Saving Throw: DC 14. "
        "Second Effect. Wisdom Saving Throw: DC 14."
    )

    assert source_action_save_count(actions) == 2
