from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_level17_profile import build_karnok_stoneward_level17_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import _karnok_profile


def test_fighter_level_seventeen_is_a_resource_delta_from_level_sixteen() -> None:
    karnok = build_karnok_stoneward_level(17)
    profile = build_karnok_stoneward_level17_profile()
    combat_profile = _karnok_profile(17)
    audits = {item.feature_id: item for item in profile.feature_audits}
    resources = dict(combat_profile.resources)

    assert karnok.level == 17
    assert karnok.proficiency_bonus == 6
    assert resources["action-surge"] == 2
    assert resources["indomitable"] == 3
    assert resources["second-wind"] == 4
    assert karnok.progression_features.critical_hit_minimum == 18
    assert audits["action-surge-two-uses"].automated is True

    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, karnok) == []
    assert_character_build_raw_ready(profile, karnok)
    assert audit_pregen_combat_stats(karnok, combat_profile) == []
    assert_pregen_combat_stats(karnok, combat_profile)
    assert_character_resources_raw_ready(karnok, profile, combat_profile)
    registry = build_certified_hero_registry()
    assert registry[("fighter", 17, "canonical")] == ("Karnok Stoneward", "karnok-stoneward-l17")
    assert ("fighter", 18, "canonical") not in registry
