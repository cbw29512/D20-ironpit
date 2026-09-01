from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level8_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_fighter_level_eight_snapshot_applies_constitution_asi_and_preserves_champion_features() -> None:
    karnok = build_karnok_stoneward_level(8)
    greatsword = karnok.weapon_attack
    shortbow = karnok.alternate_weapon_attacks[0]
    resources = {item.id: item.max_uses for item in karnok.resources}

    assert (karnok.id, karnok.level, karnok.max_hp, karnok.armor_class, karnok.speed_ft) == (
        "karnok-stoneward-l8", 8, 84, 17, 30,
    )
    assert (greatsword.attack_bonus, greatsword.damage_bonus, greatsword.damage_die_minimum) == (8, 5, 3)
    assert (shortbow.attack_bonus, shortbow.damage_bonus, shortbow.damage_die_minimum) == (4, 1, None)
    assert karnok.saving_throw_bonuses["strength"] == 8
    assert karnok.saving_throw_bonuses["constitution"] == 7
    assert karnok.skill_bonuses["athletics"] == 8
    assert resources == {
        "second-wind": 3, "action-surge": 1, "adrenaline-rush": 3, "relentless-endurance": 1,
    }
    assert karnok.progression_features.great_weapon_fighting is True
    assert karnok.progression_features.critical_hit_minimum == 19
    assert karnok.progression_features.tactical_shift_fraction == 0.5
    assert karnok.attack_action is not None and len(karnok.attack_action.slots) == 2


def test_fighter_level_eight_profile_fingerprint_resources_and_registry_pass_all_gates() -> None:
    template = build_karnok_stoneward_level(8)
    profile = build_karnok_stoneward_level8_profile()
    combat_profile = build_pregen_combat_profiles()[template.id]

    assert profile.final_ability_scores.model_dump() == {
        "strength": 20, "dexterity": 13, "constitution": 18,
        "intelligence": 10, "wisdom": 10, "charisma": 10,
    }
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [
        ("strength", 1), ("constitution", 1), ("strength", 2), ("constitution", 2),
    ]
    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    assert build_certified_hero_registry()[("fighter", 8, "canonical")] == (
        "Karnok Stoneward", "karnok-stoneward-l8",
    )
