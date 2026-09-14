from enrich_2014_failure_margin_saves import parse_failure_margin_save


def main() -> None:
    text = (
        "and the target must succeed on a DC 10 Constitution saving throw or be poisoned for 1 minute. "
        "If the saving throw fails by 5 or more, the target is instead poisoned for 5 (1d10) minutes "
        "and unconscious while poisoned in this way."
    )
    parsed = parse_failure_margin_save(text)
    assert parsed is not None
    assert parsed["save_ability"] == "constitution"
    assert parsed["dc"] == 10
    assert parsed["condition_id"] == "poisoned"
    assert parsed["duration_rounds"] == 10
    escalation = parsed["failure_margin_escalation"]
    assert escalation["margin"] == 5
    assert escalation["additional_condition_ids"] == ["unconscious"]
    assert escalation["replacement_duration_dice_count"] == 1
    assert escalation["replacement_duration_dice_size"] == 10
    assert escalation["replacement_duration_round_multiplier"] == 10
    print("2014 failure-margin save parser regression passed.")


if __name__ == "__main__":
    main()
