from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_high_level_profile import build_karnok_stoneward_level17_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_fighter_level_seventeen_is_a_delta_from_level_sixteen() -> None:
    previous = build_karnok_stoneward_level(16)
    karnok = build_karnok_stoneward_level(17)
    profile = build_karnok_stoneward_level17_profile()
    combat_profile = build_pregen_combat_profiles()[karnok.id]
    resources = {item.id: item.max_uses for item in karnok.resources}
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert (previous.ability_scores, previous.armor_class) == (karnok.ability_scores, karnok.armor_class)
    assert (karnok.level, karnok.max_hp, karnok.proficiency_bonus) == (17, 191, 6)
    assert resources["action-surge"] == 2
    assert resources["indomitable"] == 3
    assert karnok.progression_features.critical_hit_minimum == 18
    assert audits["action-surge-two-uses"].automated is True
    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, karnok) == []
    assert_character_build_raw_ready(profile, karnok)
    assert audit_pregen_combat_stats(karnok, combat_profile) == []
    assert_pregen_combat_stats(karnok, combat_profile)
    assert_character_resources_raw_ready(karnok, profile, combat_profile)
    assert build_certified_hero_registry()[("fighter", 17, "canonical")] == (
        "Karnok Stoneward", "karnok-stoneward-l17",
    )
    assert ("fighter", 18, "canonical") not in build_certified_hero_registry()
