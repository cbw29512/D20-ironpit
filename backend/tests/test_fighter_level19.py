from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_high_level_profiles import build_karnok_stoneward_level19_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_fighter_level_nineteen_snapshot_applies_combat_prowess() -> None:
    karnok = build_karnok_stoneward_level(19)
    resources = {item.id: item.max_uses for item in karnok.resources}
    shortbow = next(item for item in karnok.alternate_weapon_attacks if item.id == "karnok-shortbow")

    assert (karnok.id, karnok.level, karnok.max_hp, karnok.armor_class) == (
        "karnok-stoneward-l19", 19, 213, 17,
    )
    assert karnok.ability_scores.dexterity == 18
    assert karnok.initiative_bonus == 4
    assert karnok.weapon_attack.attack_bonus == 11
    assert shortbow.attack_bonus == 10
    assert karnok.progression_features.peerless_aim is True
    assert karnok.attack_action is not None and len(karnok.attack_action.slots) == 3
    assert resources == {
        "second-wind": 4, "action-surge": 2, "indomitable": 3,
        "adrenaline-rush": 6, "relentless-endurance": 1,
    }


def test_fighter_level_nineteen_earns_existing_certification_gates() -> None:
    template = build_karnok_stoneward_level(19)
    profile = build_karnok_stoneward_level19_profile()
    combat_profile = build_pregen_combat_profiles()[template.id]
    audits = {item.feature_id: item for item in profile.feature_audits}
    registry = build_certified_hero_registry()

    assert profile.final_ability_scores.dexterity == 18
    assert audits["boon-combat-prowess"].automated is True
    assert "Peerless Aim" in (audits["boon-combat-prowess"].notes or "")
    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    assert registry[("fighter", 19, "canonical")] == (
        "Karnok Stoneward", "karnok-stoneward-l19",
    )
