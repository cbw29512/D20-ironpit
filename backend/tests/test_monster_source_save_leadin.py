from app.content.monster_source_save_candidates import source_save_candidates


def test_save_parser_accepts_one_descriptive_sentence_before_save_clause() -> None:
    row = {
        "name": "Test Hewer",
        "actions": (
            "Boulder Toss (Recharge 6). The creature hurls a boulder at a point it can see within 90 feet. "
            "Dexterity Saving Throw: DC 17, each creature in a 5-foot-radius Sphere centered on that point. "
            "Failure: 24 (7d6) Bludgeoning damage. If the target is a Large or smaller creature, "
            "it has the Prone condition. Success: Half damage only."
        ),
        "bonusActions": "",
    }

    actions, resources = source_save_candidates(row)

    assert len(actions) == 1
    assert actions[0].name == "Boulder Toss"
    assert actions[0].save_ability == "dexterity"
    assert actions[0].dc == 17
    assert actions[0].area is not None
    assert actions[0].area.shape == "radius"
    assert actions[0].area.radius_ft == 5
    assert actions[0].range_ft == 90
    assert actions[0].resource_id == "srd-test-hewer-boulder-toss"
    assert len(resources) == 1
    assert resources[0].recharge is not None
    assert resources[0].recharge.minimum_roll == 6
