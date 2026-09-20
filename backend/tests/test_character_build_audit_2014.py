from app.content.barbarian_berserker_2014_profile import build_rokhan_stonefury_2014_profile
from app.content.barbarian_berserker_2014_runtime import build_rokhan_stonefury_2014
from app.content.build_audit import audit_character_build
from app.content.fighter_champion_2014_profile import build_karnok_stoneward_2014_profile
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.domain.character_builds import AbilityIncrease


def test_2014_karnok_profiles_match_runtime_through_level_twenty() -> None:
    for level in range(1, 21):
        profile = build_karnok_stoneward_2014_profile(level)
        template = build_karnok_stoneward_2014(level)
        assert profile.ruleset == "2014"
        assert template.ruleset == "2014"
        assert profile.final_ability_scores == template.ability_scores
        assert profile.weapon_masteries == []
        assert audit_character_build(profile, template) == []


def test_2014_raw_feature_can_raise_ability_score_maximum() -> None:
    profile = build_rokhan_stonefury_2014_profile(20)
    template = build_rokhan_stonefury_2014(20)
    assert profile.final_ability_scores.strength == 24
    assert profile.final_ability_scores.constitution == 24
    assert profile.ability_score_maximums == {"strength": 24, "constitution": 24}
    assert audit_character_build(profile, template) == []


def test_2014_score_above_twenty_fails_without_declared_raw_maximum() -> None:
    profile = build_rokhan_stonefury_2014_profile(20).model_copy(update={"ability_score_maximums": {}})
    template = build_rokhan_stonefury_2014(20)
    issues = audit_character_build(profile, template)
    assert "final-strength-exceeds-20" in issues
    assert "final-constitution-exceeds-20" in issues


def test_2014_human_uses_species_increases_not_2024_background_increases() -> None:
    profile = build_karnok_stoneward_2014_profile(1)
    assert profile.origin_feat_id is None
    assert profile.origin_feat_name is None
    assert profile.background_allowed_abilities == []
    assert profile.background_increases == []
    assert len(profile.species_increases) == 6
    assert {increase.ability for increase in profile.species_increases} == {
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
    }
    assert all(increase.amount == 1 for increase in profile.species_increases)


def test_2014_audit_rejects_2024_origin_rules_leaking_backward() -> None:
    profile = build_karnok_stoneward_2014_profile(1)
    template = build_karnok_stoneward_2014(1)
    profile.origin_feat_id = "savage-attacker"
    profile.origin_feat_name = "Savage Attacker"
    profile.background_allowed_abilities = ["strength", "dexterity", "constitution"]
    profile.background_increases = [
        AbilityIncrease(ability="strength", amount=2),
        AbilityIncrease(ability="constitution", amount=1),
    ]
    issues = audit_character_build(profile, template)
    assert "2014-origin-feat-not-allowed" in issues
    assert "2014-background-ability-increases-not-allowed" in issues


def test_ruleset_mismatch_fails_closed() -> None:
    profile = build_karnok_stoneward_2014_profile(1)
    template = build_karnok_stoneward_2014(1).model_copy(update={"ruleset": "2024"})
    assert "runtime-ruleset-mismatch" in audit_character_build(profile, template)
