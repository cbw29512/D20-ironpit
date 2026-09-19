import pytest

from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_high_level_profile import (
    build_karnok_stoneward_level16_profile,
    build_karnok_stoneward_level17_profile,
)
from app.content.fighter_progression import (
    build_karnok_stoneward_level,
    unsupported_fighter_engine_features,
)
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


def test_fighter_level_sixteen_certifies_dexterity_asi_and_sixth_mastery() -> None:
    profile = build_karnok_stoneward_level16_profile()
    template = build_karnok_stoneward_level(16)
    shortbow = next(item for item in template.alternate_weapon_attacks if item.id == "karnok-shortbow")
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert (template.level, template.max_hp, template.initiative_bonus) == (16, 180, 3)
    assert template.ability_scores.dexterity == 17
    assert (shortbow.attack_bonus, shortbow.damage_bonus) == (8, 3)
    assert len(template.weapon_masteries) == 6
    assert template.progression_features.critical_hit_minimum == 18
    assert audits["ability-score-improvement-l16"].automated is True
    _assert_certified(16, profile)


def test_fighter_level_seventeen_certifies_resource_use_increases() -> None:
    assert unsupported_fighter_engine_features(17) == ()
    profile = build_karnok_stoneward_level17_profile()
    template = build_karnok_stoneward_level(17)
    resources = {item.id: item.max_uses for item in template.resources}
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert (template.level, template.max_hp, template.weapon_attack.attack_bonus) == (17, 191, 11)
    assert template.progression_features.critical_hit_minimum == 18
    assert resources["action-surge"] == 2
    assert resources["indomitable"] == 3
    assert resources["adrenaline-rush"] == 6
    assert template.attack_action is not None and len(template.attack_action.slots) == 3
    assert audits["fighter-resource-progression-l17"].automated is True
    _assert_certified(17, profile)


def test_fighter_level_eighteen_stays_fail_closed_on_2024_survivor() -> None:
    assert set(unsupported_fighter_engine_features(18)) == {
        "survivor-defy-death",
        "survivor-heroic-rally",
    }
    with pytest.raises(ValueError, match="survivor-defy-death"):
        build_karnok_stoneward_level(18)
