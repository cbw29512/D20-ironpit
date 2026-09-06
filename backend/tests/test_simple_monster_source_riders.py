from app.content.simple_monster_source_riders import parse_hit_riders


def test_parses_target_turn_timed_condition() -> None:
    effects = parse_hit_riders(
        "Hit: 16 (3d8 + 3) Bludgeoning damage, and the target has the Poisoned condition until the end of its next turn."
    )
    assert {
        "kind": "condition",
        "condition": "poisoned",
        "expiry_timing": "target_turn_end",
    } in effects


def test_parses_source_turn_timed_condition() -> None:
    effects = parse_hit_riders(
        "Hit: 6 (1d8 + 2) Piercing damage, and the target has the Poisoned condition until the end of the merrow’s next turn."
    )
    assert {
        "kind": "condition",
        "condition": "poisoned",
        "expiry_timing": "source_turn_end",
    } in effects


def test_does_not_parse_save_dependent_condition_as_unconditional() -> None:
    effects = parse_hit_riders(
        "Hit: 6 (1d8 + 2) Piercing damage, and the target must succeed on a DC 13 Constitution saving throw or the target has the Poisoned condition until the end of its next turn."
    )
    assert not any(effect.get("kind") == "condition" for effect in effects)
