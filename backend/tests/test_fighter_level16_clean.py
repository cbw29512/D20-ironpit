from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.fighter_high_level_profile import build_karnok_stoneward_level16_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_fighter_level_sixteen_applies_audited_dexterity_asi() -> None:
    karnok = build_karnok_stoneward_level(16)
    profile = build_karnok_stoneward_level16_profile()
    combat_profile = build_pregen_combat_profiles()[karnok.id]
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert karnok.level == 16
    assert profile.final_ability_scores.dexterity == 17
    assert audits["ability-score-improvement-l16"].automated is True
    assert karnok.progression_features.critical_hit_minimum == 18

    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, karnok) == []
    assert_character_build_raw_ready(profile, karnok)
    assert audit_pregen_combat_stats(karnok, combat_profile) == []
    assert_pregen_combat_stats(karnok, combat_profile)
    assert_character_resources_raw_ready(karnok, profile, combat_profile)
