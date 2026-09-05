from app.content.iron_pit_mvp_scope import (
    affects_mvp_combat_math,
    direct_combat_math_reasons,
    movement_only_for_mvp,
)


def test_damage_and_defense_math_are_in_scope():
    assert affects_mvp_combat_math("Hit: 10 (2d6 + 3) Fire damage.")
    assert affects_mvp_combat_math("The target has Resistance to Fire damage.")
    assert "damage" in direct_combat_math_reasons("The target is immune to Cold damage.")


def test_save_needs_an_outcome_changing_consequence():
    assert not affects_mvp_combat_math("Strength Saving Throw: DC 14. Failure: The target is pushed 15 feet away.")
    assert affects_mvp_combat_math("Wisdom Saving Throw: DC 13. Failure: The target has the Frightened condition.")
    assert affects_mvp_combat_math("Dexterity Saving Throw: DC 15. Failure: 21 Fire damage. Success: Half damage.")


def test_movement_only_effects_are_non_blocking_for_mvp():
    examples = [
        "The target's Speed decreases by 10 feet until the end of its next turn.",
        "The target is pushed up to 15 feet straight away.",
        "The target is pulled up to 20 feet toward the monster.",
        "The monster teleports up to 30 feet.",
        "The monster has a Climb Speed of 40 feet.",
        "The target has the Grappled condition (escape DC 13).",
    ]
    for text in examples:
        assert not affects_mvp_combat_math(text), text
        assert movement_only_for_mvp(text), text


def test_movement_relationship_becomes_relevant_when_math_depends_on_it():
    text = "Dexterity Saving Throw: DC 15, one creature Grappled by the monster. Failure: 10 Bludgeoning damage."
    reasons = direct_combat_math_reasons(text)
    assert "targeting" in reasons
    assert "damage" in reasons


def test_direct_d20_hp_ac_action_and_condition_math_are_in_scope():
    examples = [
        "The target has Disadvantage on the next attack roll it makes.",
        "The monster has Advantage on saving throws against magical effects.",
        "The monster gains 10 Temporary Hit Points.",
        "The monster adds 3 to its AC against that attack.",
        "The target can't take an Action until the end of its next turn.",
        "The target has the Prone condition.",
        "The attack is a Critical Hit on a roll of 19 or 20.",
    ]
    for text in examples:
        assert affects_mvp_combat_math(text), text


def test_noncombat_advantage_does_not_become_combat_math():
    assert not affects_mvp_combat_math("The monster has Advantage on Wisdom (Perception) checks.")
    assert not affects_mvp_combat_math("The monster has Advantage on checks made to jump.")
