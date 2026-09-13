from import_2014_attack_details import parse_on_hit_control


def main() -> int:
    cases = [
        (
            "The target is grappled (escape DC 11). The crab has two claws, each of which can grapple only one target",
            11,
        ),
        (
            "The target is grappled (escape DC 19), and the roc can't use its talons on another target",
            19,
        ),
    ]
    for text, dc in cases:
        control, forbid, residual = parse_on_hit_control(text)
        assert control == {"grapple_escape_dc": dc, "restrains_while_grappled": False}
        assert forbid is True
        assert residual == ""
    print("2014 single-target grapple parser regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
