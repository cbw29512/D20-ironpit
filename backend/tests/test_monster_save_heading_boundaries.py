from app.content.monster_source_save_candidates import _parse_text


def test_save_parser_promotes_nearer_plain_action_heading() -> None:
    text = (
        "Bite. Melee Attack Roll: +6, reach 10 ft. Hit: 11 (2d6 + 4) Piercing damage. "
        "Constrict. Strength Saving Throw: DC 14, one Large or smaller creature within 10 feet. "
        "Failure: 13 (2d8 + 4) Bludgeoning damage."
    )

    actions, resources = _parse_text("Giant Constrictor Snake", text, "action")

    assert [action.name for action in actions] == ["Constrict"]
    assert actions[0].id == "srd-giant-constrictor-snake-constrict"
    assert resources == []


def test_save_parser_promotes_nearer_recharge_heading_and_resource() -> None:
    text = (
        "Bite. Melee Attack Roll: +5, reach 5 ft. Hit: 10 (2d6 + 3) Slashing damage plus 3 (1d6) Acid damage. "
        "Acid Spray (Recharge 6). Dexterity Saving Throw: DC 12, each creature in a 30-foot-long, 5-foot-wide Line. "
        "Failure: 14 (4d6) Acid damage. Success: Half damage."
    )

    actions, resources = _parse_text("Ankheg", text, "action")

    assert [action.name for action in actions] == ["Acid Spray"]
    assert actions[0].resource_id == "srd-ankheg-acid-spray"
    assert len(resources) == 1
    assert resources[0].recharge is not None
    assert resources[0].recharge.minimum_roll == 6
