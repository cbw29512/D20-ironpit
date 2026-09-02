from app.combat.state import build_combatant_state, refresh_start_of_turn
from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_level10_combat_profile import build_karnok_stoneward_level10_combat_profile
from app.content.fighter_level10_profile import build_karnok_stoneward_level10_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_fighter_level_ten_snapshot_is_derived_from_level_nine() -> None:
    karnok = build_karnok_stoneward_level(10)
    greatsword = karnok.weapon_attack
    shortbow = karnok.alternate_weapon_attacks[0]
    resources = {item.id: item.max_uses for item in karnok.resources}

    assert (karnok.id, karnok.level, karnok.max_hp, karnok.armor_class, karnok.speed_ft) == (
        "karnok-stoneward-l10", 10, 104, 17, 30,
    )
    assert (greatsword.attack_bonus, greatsword.damage_bonus, greatsword.damage_die_minimum) == (9, 5, 3)
    assert (shortbow.attack_bonus, shortbow.damage_bonus) == (5, 1)
    assert karnok.saving_throw_bonuses["strength"] == 9
    assert karnok.saving_throw_bonuses["constitution"] == 8
    assert karnok.skill_bonuses["athletics"] == 9
    assert karnok.weapon_masteries == ["flail", "javelin", "spear", "greatsword", "shortbow"]
    assert resources == {
        "second-wind": 4, "action-surge": 1, "indomitable": 1,
        "adrenaline-rush": 4, "relentless-endurance": 1,
    }
    assert karnok.progression_features.indomitable_bonus == 10
    assert karnok.progression_features.tactical_master_sap_weapon_ids == ["greatsword"]
    assert karnok.progression_features.heroic_warrior is True
    assert karnok.attack_action is not None and len(karnok.attack_action.slots) == 2


def test_fighter_level_ten_passes_build_fingerprint_resource_and_public_registry_gates() -> None:
    template = build_karnok_stoneward_level(10)
    profile = build_karnok_stoneward_level10_profile()
    combat_profile = build_karnok_stoneward_level10_combat_profile()
    registered_profile = build_pregen_combat_profiles()[template.id]

    assert registered_profile == combat_profile
    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    assert build_certified_hero_registry()[("fighter", 10, "canonical")] == (
        "Karnok Stoneward", "karnok-stoneward-l10",
    )


def test_fighter_level_ten_turn_start_receives_heroic_inspiration() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(10))
    assert state.heroic_inspiration is False
    refresh_start_of_turn(state)
    assert state.heroic_inspiration is True
