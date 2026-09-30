from __future__ import annotations

from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package


def test_2024_druid_level_one_is_legal_magician_foundation() -> None:
    profile = build_thalen_greenbough_profile(1)
    hero = build_thalen_greenbough_level(1)

    assert_canonical_profile_policy(profile)
    assert profile.ruleset == "2024"
    assert profile.class_id == "druid"
    assert profile.subclass_id is None
    assert profile.subclass_name is None
    assert profile.species_id == "wood-elf"
    assert profile.background_id == "acolyte"
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma, hero.ability_scores.intelligence) == (17, 15, 13)
    assert (hero.ability_scores.strength, hero.ability_scores.dexterity, hero.ability_scores.constitution) == (10, 10, 10)
    assert hero.armor_class == 13
    assert hero.max_hp == 8
    assert hero.speed_ft == 35
    assert hero.weapon_attack is not None
    assert hero.weapon_attack.weapon.id == "sickle"
    assert hero.weapon_attack.weapon.mastery_property is None
    assert hero.weapon_attack.attack_bonus == 2
    assert hero.saving_throw_bonuses["intelligence"] == 3
    assert hero.saving_throw_bonuses["wisdom"] == 5
    assert hero.skill_bonuses["nature"] == 6
    assert hero.skill_bonuses["perception"] == 5
    assert {item.id: item.max_uses for item in hero.resources} == {"spell-slot-1": 2}


def test_2024_druid_level_one_has_no_early_circle_of_land_features() -> None:
    profile = build_thalen_greenbough_profile(1)

    assert profile.subclass_id is None
    assert all("circle" not in item.feature_id for item in profile.feature_audits)
    assert all("land" not in item.feature_id for item in profile.feature_audits)


def test_2024_druid_level_one_reuses_universal_fey_ancestry() -> None:
    hero = build_thalen_greenbough_level(1)

    grants = hero.progression_features.saving_throw_advantage_grants
    assert len(grants) == 1
    grant = grants[0]
    assert grant.source_id == "fey-ancestry"
    assert set(grant.abilities) == {
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
    }
    assert grant.required_effect_tags == ["charm"]


def test_2024_druid_level_one_spell_package_is_edition_correct() -> None:
    package = canonical_spell_package("druid", 1, "2024", 3)

    assert package is not None
    assert [item.id for item in package.cantrips] == [
        "poison-spray", "elementalism", "mending",
    ]
    assert [item.id for item in package.spells] == [
        "healing-word", "cure-wounds", "longstrider", "detect-magic",
    ]
    assert [item.id for item in package.always_prepared_spells] == [
        "speak-with-animals",
    ]

    hero = build_thalen_greenbough_level(1)
    poison = hero.spell_attack_actions[0]
    assert (
        poison.id,
        poison.action_cost,
        poison.attack_kind,
        poison.range_ft,
        poison.attack_bonus,
        poison.damage_dice_count,
        poison.damage_dice_size,
        poison.damage_type,
    ) == ("poison-spray", "action", "ranged", 30, 5, 1, 12, "poison")

    assert [item.id for item in hero.healing_actions] == ["healing-word", "cure-wounds"]
    healing_word, cure_wounds = hero.healing_actions
    assert (healing_word.dice_count, healing_word.dice_size, healing_word.healing_bonus) == (2, 4, 3)
    assert (cure_wounds.dice_count, cure_wounds.dice_size, cure_wounds.healing_bonus) == (2, 8, 3)

    longstrider = hero.defensive_spell_actions[0]
    assert (
        longstrider.id,
        longstrider.action_cost,
        longstrider.range_ft,
        longstrider.duration_minutes,
        longstrider.target_count,
        longstrider.target_count_per_slot_above,
        longstrider.concentration,
    ) == ("longstrider", "action", 5, 60, 1, 1, False)
