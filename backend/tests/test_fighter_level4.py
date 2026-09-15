from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.fighter_progression_profile import build_karnok_stoneward_level4_profile
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_karnok_stoneward_level4_combat_profile


def test_fighter_level_four_snapshot_has_raw_advancement() -> None:
    karnok = build_karnok_stoneward_level(4)
    resources = {resource.id: resource.max_uses for resource in karnok.resources}

    assert (karnok.id, karnok.level, karnok.max_hp) == ("karnok-stoneward-l4", 4, 40)
    assert (karnok.weapon_attack.attack_bonus, karnok.weapon_attack.damage_bonus) == (6, 4)
    assert karnok.saving_throw_bonuses["strength"] == 6
    assert karnok.saving_throw_bonuses["constitution"] == 5
    assert karnok.skill_bonuses["athletics"] == 6
    assert resources["second-wind"] == 3
    assert resources["action-surge"] == 1
    assert resources["adrenaline-rush"] == 2
    assert len(karnok.weapon_masteries) == 4
    assert karnok.weapon_masteries == ["flail", "javelin", "spear", "longsword"]


def test_fighter_level_four_inherits_champion_level_three_features() -> None:
    features = build_karnok_stoneward_level(4).progression_features

    assert features.critical_hit_minimum == 19
    assert features.initiative_advantage is True
    assert features.athletics_advantage is True
    assert features.critical_move_fraction == 0.5


def test_fighter_level_four_profile_declares_split_asi_and_passes_structural_audit() -> None:
    template = build_karnok_stoneward_level(4)
    profile = build_karnok_stoneward_level4_profile()

    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [
        ("strength", 1),
        ("constitution", 1),
    ]
    assert profile.final_ability_scores.strength == 18
    assert profile.final_ability_scores.constitution == 16
    assert profile.weapon_masteries == template.weapon_masteries
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)


def test_fighter_level_four_runtime_matches_candidate_combat_fingerprint() -> None:
    template = build_karnok_stoneward_level(4)
    combat_profile = build_karnok_stoneward_level4_combat_profile()

    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)


def test_fighter_level_eighteen_runtime_includes_survivor_engine_fields() -> None:
    assert build_karnok_stoneward_level(15).progression_features.critical_hit_minimum == 18
    assert build_karnok_stoneward_level(17).level == 17

    level_eighteen = build_karnok_stoneward_level(18)
    features = level_eighteen.progression_features

    assert level_eighteen.level == 18
    assert features.death_save_advantage is True
    assert features.death_save_recovery_minimum == 18
    assert features.bloodied_start_turn_healing_base == 5
    assert features.bloodied_start_turn_healing_add_constitution is True
