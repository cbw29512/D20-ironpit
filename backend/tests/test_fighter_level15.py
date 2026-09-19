from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_high_level_profile import build_karnok_stoneward_level15_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_fighter_level_fifteen_reuses_universal_superior_critical_threshold() -> None:
    karnok = build_karnok_stoneward_level(15)
    profile = build_karnok_stoneward_level15_profile()
    combat_profile = build_pregen_combat_profiles()[karnok.id]
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert karnok.level == 15
    assert karnok.progression_features.critical_hit_minimum == 18
    assert audits["superior-critical"].automated is True
    assert "Superior Critical" in audits["superior-critical"].feature_name

    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, karnok) == []
    assert_character_build_raw_ready(profile, karnok)
    assert audit_pregen_combat_stats(karnok, combat_profile) == []
    assert_pregen_combat_stats(karnok, combat_profile)
    assert_character_resources_raw_ready(karnok, profile, combat_profile)
    registry = build_certified_hero_registry()
    assert registry[("fighter", 15, "canonical")] == (
        "Karnok Stoneward",
        "karnok-stoneward-l15",
    )
    assert ("fighter", 16, "canonical") not in registry
