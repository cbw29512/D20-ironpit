from scripts.report_zero_engine_monsters import _unmodeled_action_rider


def test_supported_universal_attack_riders_are_not_reported_as_unmodeled() -> None:
    supported = [
        "Hit: 7 Slashing damage, and the target's Speed decreases by 10 feet until the end of its next turn.",
        "Hit: 7 Slashing damage, and the target has Disadvantage on the next attack roll it makes before the end of its next turn.",
        "Hit: 7 Slashing damage, and the next attack roll made against the target before the start of the wolf's next turn has Advantage.",
        "Hit: 7 Necrotic damage, and the target's Hit Point maximum decreases by an amount equal to the Necrotic damage taken.",
        "Hit: 7 Necrotic damage, and the target's Hit Point maximum decreases by an amount equal to the damage taken.",
    ]

    for action_text in supported:
        assert _unmodeled_action_rider(action_text) is False


def test_genuinely_unmodeled_attack_riders_still_fail_closed() -> None:
    unsupported = [
        "Hit: 4 Piercing damage, and the stirge attaches to the target.",
        "Hit or Miss: The target is pushed 10 feet.",
    ]

    for action_text in unsupported:
        assert _unmodeled_action_rider(action_text) is True
