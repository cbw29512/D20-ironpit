from app.content.monster_combat_scope import combat_math_relevant


def test_non_provoking_movement_is_arena_neutral_without_hiding_real_attacks() -> None:
    bubble_dash = (
        "Bubble Dash. While underwater, the creature moves up to half its Swim Speed "
        "without provoking Opportunity Attacks."
    )
    flyby = "Flyby. The creature doesn't provoke an Opportunity Attack when it flies out of an enemy's reach."
    riposte = "Riposte. On a miss, the creature makes one Rapier attack against the triggering creature."

    assert combat_math_relevant(bubble_dash) is False
    assert combat_math_relevant(flyby) is False
    assert combat_math_relevant(riposte) is True
