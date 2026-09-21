from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.fighter_high_level_profile import build_karnok_stoneward_level17_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_fighter_level_seventeen_reuses_shared_resource_progression() -> None:
    karnok = build_karnok_stoneward_level(17)
    profile = build_karnok_stoneward_level17_profile()
    combat_profile = build_pregen_combat_profiles()[karnok.id]
    resources = {item.id: item.max_uses for item in karnok.resources}

    assert karnok.level == 17
    assert resources["action-surge"] == 2
    assert resources["indomitable"] == 3
    assert resources["second-wind"] == 4
    assert karnok.progression_features.critical_hit_minimum == 18

    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, karnok) == []
    assert_character_build_raw_ready(profile, karnok)
    assert audit_pregen_combat_stats(karnok, combat_profile) == []
    assert_pregen_combat_stats(karnok, combat_profile)
    assert_character_resources_raw_ready(karnok, profile, combat_profile)
