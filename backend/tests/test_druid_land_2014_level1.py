from __future__ import annotations

from app.content.druid_land_2014_profile import build_thalen_greenbough_2014_profile
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014


def test_thalen_level_one_is_persistent_wood_elf_acolyte_druid() -> None:
    profile = build_thalen_greenbough_2014_profile(1)
    hero = build_thalen_greenbough_2014(1)

    assert (profile.species_id, profile.background_id, profile.class_id) == (
        "wood-elf", "acolyte", "druid",
    )
    assert profile.final_ability_scores.model_dump() == {
        "strength": 8,
        "dexterity": 15,
        "constitution": 14,
        "intelligence": 12,
        "wisdom": 16,
        "charisma": 10,
    }
    assert hero.ability_scores == profile.final_ability_scores
    assert hero.max_hp == 10
    assert hero.armor_class == 15
    assert hero.speed_ft == 35
    assert hero.initiative_bonus == 2


def test_thalen_level_one_runtime_binds_only_supported_combat_options() -> None:
    hero = build_thalen_greenbough_2014(1)

    assert hero.weapon_attack.weapon.id == "scimitar"
    assert hero.weapon_attack.attack_bonus == 4
    assert hero.weapon_attack.damage_bonus == 2
    assert {spell.id for spell in hero.spell_attack_actions} == {"produce-flame"}
    assert {spell.id for spell in hero.spell_save_actions} == {"poison-spray"}
    assert {spell.id for spell in hero.defensive_spell_actions} == {"longstrider"}
    assert {action.id for action in hero.healing_actions} == {"healing-word", "cure-wounds"}
    assert {resource.id: resource.max_uses for resource in hero.resources} == {"spell-slot-1": 2}


def test_thalen_fey_ancestry_reuses_contextual_save_advantage() -> None:
    hero = build_thalen_greenbough_2014(1)
    grant = hero.progression_features.saving_throw_advantage_grants[0]

    assert grant.source_id == "fey-ancestry"
    assert grant.required_effect_tags == ["charm"]
    assert set(grant.abilities) == {
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
    }
