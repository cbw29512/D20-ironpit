from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_high_level_profiles import build_karnok_stoneward_level20_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_fighter_level_twenty_uses_four_shared_attack_slots() -> None:
    karnok = build_karnok_stoneward_level(20)

    assert (karnok.id, karnok.level, karnok.max_hp, karnok.armor_class) == (
        "karnok-stoneward-l20", 20, 224, 17,
    )
    assert karnok.ability_scores.dexterity == 18
    assert karnok.attack_action is not None
    assert len(karnok.attack_action.slots) == 4


def test_fighter_level_twenty_passes_profile_fingerprint_and_registry_gates() -> None:
    template = build_karnok_stoneward_level(20)
    profile = build_karnok_stoneward_level20_profile()
    combat_profile = build_pregen_combat_profiles()[template.id]
    audits = {item.feature_id: item for item in profile.feature_audits}
    registry = build_certified_hero_registry()

    assert audits["extra-attack-4"].automated is True
    assert combat_profile.level == 20
    assert combat_profile.max_hp == 224
    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    assert registry[("fighter", 20, "canonical")] == (
        "Karnok Stoneward", "karnok-stoneward-l20",
    )