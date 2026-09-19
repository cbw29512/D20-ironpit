from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_high_level_profile import (
    build_karnok_stoneward_level13_profile,
    build_karnok_stoneward_level14_profile,
)
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def _assert_certified(level: int, profile) -> None:
    template = build_karnok_stoneward_level(level)
    combat_profile = build_pregen_combat_profiles()[template.id]

    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    assert build_certified_hero_registry()[("fighter", level, "canonical")] == (
        "Karnok Stoneward",
        f"karnok-stoneward-l{level}",
    )


def test_fighter_level_thirteen_certifies_studied_attacks_and_second_indomitable_use() -> None:
    karnok = build_karnok_stoneward_level(13)
    profile = build_karnok_stoneward_level13_profile()
    resources = {item.id: item.max_uses for item in karnok.resources}
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert (karnok.level, karnok.max_hp, karnok.weapon_attack.attack_bonus) == (13, 147, 10)
    assert karnok.saving_throw_bonuses["constitution"] == 10
    assert karnok.progression_features.studied_attacks is True
    assert resources["indomitable"] == 2
    assert resources["adrenaline-rush"] == 5
    assert karnok.attack_action is not None and len(karnok.attack_action.slots) == 3
    assert audits["studied-attacks"].automated is True
    _assert_certified(13, profile)


def test_fighter_level_fourteen_certifies_dexterity_asi_and_derived_stats() -> None:
    karnok = build_karnok_stoneward_level(14)
    profile = build_karnok_stoneward_level14_profile()
    shortbow = next(item for item in karnok.alternate_weapon_attacks if item.id == "karnok-shortbow")
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert (karnok.level, karnok.max_hp, karnok.initiative_bonus) == (14, 158, 2)
    assert karnok.ability_scores.dexterity == 15
    assert (shortbow.attack_bonus, shortbow.damage_bonus) == (7, 2)
    assert karnok.skill_bonuses["acrobatics"] == 2
    assert profile.final_ability_scores.dexterity == 15
    assert karnok.progression_features.critical_hit_minimum == 19
    assert audits["ability-score-improvement-l14"].automated is True
    _assert_certified(14, profile)
    assert ("fighter", 17, "canonical") not in build_certified_hero_registry()
