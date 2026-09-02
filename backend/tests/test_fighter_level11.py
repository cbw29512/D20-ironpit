from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_level11_combat_profile import build_karnok_stoneward_level11_combat_profile
from app.content.fighter_level11_profile import build_karnok_stoneward_level11_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_fighter_level_eleven_snapshot_has_three_attack_slots() -> None:
    karnok = build_karnok_stoneward_level(11)
    resources = {item.id: item.max_uses for item in karnok.resources}

    assert (karnok.id, karnok.level, karnok.max_hp, karnok.armor_class) == (
        "karnok-stoneward-l11", 11, 114, 17,
    )
    assert karnok.weapon_attack.attack_bonus == 9
    assert karnok.weapon_attack.damage_bonus == 5
    assert karnok.weapon_attack.damage_die_minimum == 3
    assert karnok.saving_throw_bonuses["strength"] == 9
    assert karnok.saving_throw_bonuses["constitution"] == 8
    assert karnok.weapon_masteries == ["flail", "javelin", "spear", "greatsword", "shortbow"]
    assert resources == {
        "second-wind": 4, "action-surge": 1, "indomitable": 1,
        "adrenaline-rush": 4, "relentless-endurance": 1,
    }
    assert karnok.progression_features.heroic_warrior is True
    assert karnok.attack_action is not None and len(karnok.attack_action.slots) == 3


def test_fighter_level_eleven_passes_profile_fingerprint_and_registry_gates() -> None:
    template = build_karnok_stoneward_level(11)
    profile = build_karnok_stoneward_level11_profile()
    combat_profile = build_karnok_stoneward_level11_combat_profile()
    registered_profile = build_pregen_combat_profiles()[template.id]
    audits = {item.feature_id: item for item in profile.feature_audits}
    registry = build_certified_hero_registry()

    assert registered_profile == combat_profile
    assert audits["two-extra-attacks"].automated is True
    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    assert registry[("fighter", 11, "canonical")] == (
        "Karnok Stoneward", "karnok-stoneward-l11",
    )
    assert ("fighter", 12, "canonical") not in registry
