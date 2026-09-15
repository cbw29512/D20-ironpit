from app.content.monster_source_save_count import source_action_save_count


def test_counts_initial_attack_rider_save_once() -> None:
    actions = (
        "Bite. Melee Attack Roll: +5. Hit: 7 Piercing damage. "
        "Constitution Saving Throw: DC 13. Failure: the target has the Poisoned condition."
    )
    assert source_action_save_count(actions) == 1


def test_repeat_save_wording_does_not_add_a_second_action_save() -> None:
    actions = (
        "Gaze. Wisdom Saving Throw: DC 14. Failure: the target has the Frightened condition. "
        "At the end of each of its turns, the target repeats the saving throw."
    )
    assert source_action_save_count(actions) == 1


def test_separate_top_level_save_actions_are_counted_independently() -> None:
    actions = (
        "Breath. Dexterity Saving Throw: DC 15. Failure: 21 Fire damage. "
        "Roar. Wisdom Saving Throw: DC 15. Failure: the target has the Frightened condition."
    )
    assert source_action_save_count(actions) == 2


def test_out_of_match_long_rest_save_is_not_counted_as_action_save() -> None:
    actions = (
        "Curse. Wisdom Saving Throw: DC 15. Failure: the target is cursed. "
        "After a Long Rest, the cursed creature repeats the Saving Throw: DC 15."
    )
    assert source_action_save_count(actions) == 1
