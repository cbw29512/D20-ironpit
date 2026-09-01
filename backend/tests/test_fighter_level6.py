from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level6_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_karnok_stoneward_level6_combat_profile


def test_fighter_level_six_snapshot_applies_strength_asi_and_preserves_champion_progression() -> None:
    karnok = build_karnok_stoneward_level(6)
    resources = {resource.id: resource.max_uses for resource in karnok.resources}
    attacks = {attack.id: attack for attack in [karnok.weapon_attack, *karnok.alternate_weapon_attacks]}
    features = karnok.progression_features

    assert (karnok.id, karnok.level, karnok.max_hp, karnok.armor_class, karnok.speed_ft) == (
        "karnok-stoneward-l6", 6, 58, 17, 30,
    )
    assert (attacks["karnok-greatsword"].attack_bonus, attacks["karnok-greatsword"].damage_bonus) == (8, 5)
    assert (attacks["karnok-shortbow"].attack_bonus, attacks["karnok-shortbow"].damage_bonus) == (4, 1)
    assert karnok.saving_throw_bonuses["strength"] == 8
    assert karnok.saving_throw_bonuses["constitution"] == 6
    assert karnok.skill_bonuses["athletics"] == 8
    assert resources == {
        "second-wind": 3, "action-surge": 1, "adrenaline-rush": 3, "relentless-endurance": 1,
    }
    assert karnok.weapon_masteries == ["flail", "javelin", "spear", "longsword"]
    assert features.critical_hit_minimum == 19
    assert features.initiative_advantage is True
    assert features.athletics_advantage is True
    assert features.critical_move_fraction == 0.5
    assert features.tactical_shift_fraction == 0.5
    assert karnok.attack_action is not None and len(karnok.attack_action.slots) == 2
    assert all(slot.attack_ids == ["karnok-greatsword", "karnok-shortbow"] for slot in karnok.attack_action.slots)


def test_fighter_level_six_profile_fingerprint_resources_and_registry_pass_all_gates() -> None:
    template = build_karnok_stoneward_level(6)
    profile = build_karnok_stoneward_level6_profile()
    combat_profile = build_karnok_stoneward_level6_combat_profile()

    assert profile.final_ability_scores.model_dump() == {
        "strength": 20, "dexterity": 13, "constitution": 16,
        "intelligence": 10, "wisdom": 10, "charisma": 10,
    }
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [
        ("strength", 1), ("constitution", 1), ("strength", 2),
    ]
    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    assert build_certified_hero_registry()[("fighter", 6, "canonical")] == (
        "Karnok Stoneward", "karnok-stoneward-l6",
    )
