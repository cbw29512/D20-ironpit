from import_2014_attack_details import parse_on_hit_control


def main() -> int:
    control, forbid, residual = parse_on_hit_control(
        "The target is grappled (escape DC 11). The crab has two claws, each of which can grapple only one target"
    )
    assert control == {"grapple_escape_dc": 11, "restrains_while_grappled": False}
    assert forbid is True
    assert residual == ""
    print("2014 per-limb grapple parser regression passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
