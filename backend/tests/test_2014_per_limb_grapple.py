from scripts.import_2014_attack_details import parse_on_hit_control


def test_per_limb_grapple_sentence_is_fully_consumed() -> None:
    control, forbid, residual = parse_on_hit_control(
        "The target is grappled (escape DC 11). The crab has two claws, each of which can grapple only one target"
    )
    assert control == {"grapple_escape_dc": 11, "restrains_while_grappled": False}
    assert forbid is True
    assert residual == ""
