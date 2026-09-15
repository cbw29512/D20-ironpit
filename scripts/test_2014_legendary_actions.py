from import_2014_legendary_actions import parse_legendary_actions


def _source(option: str) -> str:
    return (
        "<p>The creature can take 3 legendary actions, choosing from the options below.</p>"
        f"<p>{option}</p>"
    )


def _attack(attack_id: str, name: str) -> dict:
    return {"id": attack_id, "name": name}


def main() -> int:
    cases = [
        (
            "<strong>Claw Attack.</strong> The sphinx makes one claw attack.",
            [_attack("claw", "Claw")], "claw",
        ),
        (
            "<strong>Hooves.</strong> The unicorn makes one attack with its hooves.",
            [_attack("hooves", "Hooves")], "hooves",
        ),
        (
            "<strong>Unarmed Strike.</strong> The vampire makes one unarmed strike.",
            [_attack("unarmed-strike", "Unarmed Strike")], "unarmed-strike",
        ),
        (
            "<strong>Paralyzing Touch.</strong> The lich uses its Paralyzing Touch.",
            [_attack("paralyzing-touch", "Paralyzing Touch")], "paralyzing-touch",
        ),
    ]
    for option, attacks, expected in cases:
        uses, parsed, unsupported = parse_legendary_actions(_source(option), attacks)
        assert uses == 3
        assert unsupported == []
        assert len(parsed) == 1
        assert parsed[0]["attack_id"] == expected

    ambiguous = _source(
        "<strong>Attack.</strong> The tarrasque makes one claw attack or tail attack."
    )
    uses, parsed, unsupported = parse_legendary_actions(
        ambiguous, [_attack("claw", "Claw"), _attack("tail", "Tail")]
    )
    assert uses == 3
    assert parsed == []
    assert unsupported == ["Attack"]

    qualified = _source(
        "<strong>Unarmed Strike.</strong> The vampire makes one unarmed strike."
    )
    _, parsed, unsupported = parse_legendary_actions(
        qualified, [_attack("unarmed-strike-vampire-form-only", "Unarmed Strike (Vampire Form Only)")]
    )
    assert unsupported == []
    assert parsed[0]["attack_id"] == "unarmed-strike-vampire-form-only"

    print("2014 legendary action parser regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
