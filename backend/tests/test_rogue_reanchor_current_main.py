from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS


def test_reanchored_registry_preserves_current_fighter_and_rogue_twenty() -> None:
    progressions = {(item.class_id, item.template_builder.__name__): item for item in CERTIFIED_HERO_PROGRESSIONS}

    fighter = progressions[("fighter", "build_karnok_stoneward_level")]
    rogue2014 = progressions[("rogue", "build_mara_quickstep_2014")]

    assert tuple(fighter.levels)[-1] == 16
    assert tuple(rogue2014.levels)[-1] == 20
    assert fighter.template_builder(16).level == 16
    assert rogue2014.template_builder(20).level == 20
