import pytest

from app.content.fighter_champion_variant_profiles import (
    build_fighter_champion_variant_profile,
    fighter_champion_variant_profiles,
)
from app.content.fighter_champion_variant_specs import FIGHTER_CHAMPION_VARIANT_SPECS


def test_champion_matrix_contains_four_clone_style_lines_from_three_to_twenty() -> None:
    profiles = fighter_champion_variant_profiles()
    assert len(profiles) == 72
    assert {profile.build_id for profile in profiles} == set(FIGHTER_CHAMPION_VARIANT_SPECS)
    assert {profile.level for profile in profiles} == set(range(3, 21))
    assert {profile.character_name for profile in profiles} == {"Karnok Stoneward"}
    assert {profile.subclass_id for profile in profiles} == {"champion"}


@pytest.mark.parametrize("build_id", FIGHTER_CHAMPION_VARIANT_SPECS)
def test_each_champion_line_keeps_one_identity_and_gains_second_style_at_seven(build_id: str) -> None:
    level_three = build_fighter_champion_variant_profile(build_id, 3)
    level_seven = build_fighter_champion_variant_profile(build_id, 7)
    spec = FIGHTER_CHAMPION_VARIANT_SPECS[build_id]
    assert level_three.fighting_styles == [spec.fighting_styles[0]]
    assert level_seven.fighting_styles == list(spec.fighting_styles)
    assert level_three.fighting_style == spec.fighting_styles[0]
    assert level_seven.fighting_style == spec.fighting_styles[0]


@pytest.mark.parametrize("level,count", [(3, 3), (4, 4), (10, 5), (16, 6), (20, 6)])
def test_weapon_mastery_count_is_derived_from_fighter_level(level: int, count: int) -> None:
    for build_id, spec in FIGHTER_CHAMPION_VARIANT_SPECS.items():
        profile = build_fighter_champion_variant_profile(build_id, level)
        assert len(profile.weapon_masteries) == count
        assert profile.weapon_masteries == list(spec.mastery_priority[:count])
        assert spec.primary_weapon in profile.weapon_masteries


def test_strength_variants_finish_with_strength_and_constitution_maxed() -> None:
    for build_id in ("great-weapon", "sword-shield"):
        scores = build_fighter_champion_variant_profile(build_id, 20).final_ability_scores
        assert (scores.strength, scores.dexterity, scores.constitution) == (20, 18, 20)


def test_dexterity_variants_finish_with_dexterity_constitution_and_wisdom_focus() -> None:
    for build_id in ("archer", "dual-wield"):
        scores = build_fighter_champion_variant_profile(build_id, 20).final_ability_scores
        assert (scores.strength, scores.dexterity, scores.constitution, scores.wisdom) == (10, 20, 20, 18)


def test_level_nineteen_is_epic_boon_not_an_ordinary_asi() -> None:
    profile = build_fighter_champion_variant_profile("great-weapon", 19)
    audits = {audit.feature_id: audit for audit in profile.feature_audits}
    assert "boon-combat-prowess" in audits
    assert audits["boon-combat-prowess"].automated is False
    assert "Peerless Aim remains runtime-blocked" in (audits["boon-combat-prowess"].notes or "")


def test_high_level_character_truth_marks_only_certified_features_automated() -> None:
    profile = build_fighter_champion_variant_profile("archer", 20)
    audits = {audit.feature_id: audit for audit in profile.feature_audits}
    assert audits["tactical-master"].automated is True
    for feature_id in ("heroic-warrior", "studied-attacks", "superior-critical", "survivor"):
        assert feature_id in audits
        assert audits[feature_id].automated is False


def test_variant_builder_fails_closed_outside_champion_branch() -> None:
    with pytest.raises(ValueError):
        build_fighter_champion_variant_profile("archer", 2)
    with pytest.raises(ValueError):
        build_fighter_champion_variant_profile("unknown", 3)
