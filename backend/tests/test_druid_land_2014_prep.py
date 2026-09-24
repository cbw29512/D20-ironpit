from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.druid_land_2014_combat_profile import build_thalen_greenbough_2014_combat_profile
from app.content.druid_land_2014_profile import build_thalen_greenbough_2014_profile
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014


def test_thalen_persistent_identity_and_asi_progression_are_prepared() -> None:
    one = build_thalen_greenbough_2014_profile(1)
    twenty = build_thalen_greenbough_2014_profile(20)
    assert one.character_name == twenty.character_name == "Thalen Greenbough"
    assert one.species_id == twenty.species_id == "human"
    assert twenty.subclass_id == "circle-land"
    assert one.class_equipment == twenty.class_equipment
    assert twenty.final_ability_scores.wisdom == 20
    assert twenty.final_ability_scores.constitution == 18


def test_thalen_runtime_and_fingerprint_share_2014_slots() -> None:
    for level in (1, 2, 8, 17, 20):
        runtime = build_thalen_greenbough_2014(level)
        fingerprint = build_thalen_greenbough_2014_combat_profile(level)
        assert {item.id: item.max_uses for item in runtime.resources} == dict(fingerprint.resources)
        assert runtime.ruleset == "2014"
        assert runtime.weapon_attack.weapon.mastery_property is None


def test_wild_shape_and_land_features_remain_explicitly_uncertified() -> None:
    profile = build_thalen_greenbough_2014_profile(20)
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["wild-shape"].automated is False
    assert audits["lands-stride"].automated is False
    assert audits["natures-ward"].automated is False
    assert audits["natures-sanctuary"].automated is False
    assert audits["beast-spells"].automated is False
    assert audits["archdruid"].automated is False
    assert all(item.class_id != "druid" for item in CERTIFIED_HERO_PROGRESSIONS)
