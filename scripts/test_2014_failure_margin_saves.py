from enrich_2014_failure_margin_saves import parse_failure_margin_save


def _replacement_case() -> None:
    text = (
        "and the target must succeed on a DC 10 Constitution saving throw or be poisoned for 1 minute. "
        "If the saving throw fails by 5 or more, the target is instead poisoned for 5 (1d10) minutes "
        "and unconscious while poisoned in this way."
    )
    parsed = parse_failure_margin_save(text)
    assert parsed is not None
    escalation = parsed["failure_margin_escalation"]
    assert parsed["duration_rounds"] == 10
    assert escalation["margin"] == 5
    assert escalation["replacement_duration_dice_count"] == 1
    assert escalation["replacement_duration_dice_size"] == 10
    assert escalation["replacement_duration_round_multiplier"] == 10


def _pseudodragon_case() -> None:
    text = (
        "and the target must succeed on a DC 11 Constitution saving throw or become poisoned for 1 hour. "
        "If the saving throw fails by 5 or more, the target falls unconscious for the same duration, "
        "or until it takes damage or another creature uses an action to shake it awake."
    )
    parsed = parse_failure_margin_save(text)
    assert parsed is not None
    assert parsed["duration_rounds"] == 600
    escalation = parsed["failure_margin_escalation"]
    assert escalation == {
        "margin": 5,
        "additional_condition_ids": ["unconscious"],
        "ends_on_damage": True,
        "allowed_removal_action_ids": ["wake-sleeper"],
    }


def _sprite_case() -> None:
    text = (
        "and the target must succeed on a DC 10 Constitution saving throw or become poisoned for 1 minute. "
        "If its saving throw result is 5 or lower, the poisoned target falls unconscious for the same duration, "
        "or until it takes damage or another creature takes an action to shake it awake."
    )
    parsed = parse_failure_margin_save(text)
    assert parsed is not None
    assert parsed["dc"] == 10
    assert parsed["duration_rounds"] == 10
    assert parsed["failure_margin_escalation"]["margin"] == 5


def main() -> None:
    _replacement_case()
    _pseudodragon_case()
    _sprite_case()
    print("2014 failure-margin save parser regressions passed.")


if __name__ == "__main__":
    main()
