from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_high_level_profile import build_karnok_stoneward_level15_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_fighter_level_fifteen_certifies_superior_critical() -> None:
    profile = build_karnok_stoneward_level15_profile()
    template = build_karnok_stoneward_level(15)
    combat_profile = build_pregen_combat_profiles()[template.id]
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert (template.level, template.max_hp, template.progression_features.critical_hit_minimum) == (15, 169, 18)
    assert template.attack_action is not None and len(template.attack_action.slots) == 3
    assert template.progression_features.studied_attacks is True
    assert audits["superior-critical"].automated is True

    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    assert build_certified_hero_registry()[("fighter", 15, "canonical")] == (
        "Karnok Stoneward",
        "karnok-stoneward-l15",
    )


def test_superior_critical_changes_only_the_critical_threshold_at_level_fifteen() -> None:
    level_fourteen = build_karnok_stoneward_level(14)
    level_fifteen = build_karnok_stoneward_level(15)

    assert level_fourteen.progression_features.critical_hit_minimum == 19
    assert level_fifteen.progression_features.critical_hit_minimum == 18
    assert len(level_fourteen.attack_action.slots) == len(level_fifteen.attack_action.slots) == 3
