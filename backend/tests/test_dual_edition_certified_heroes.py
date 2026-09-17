from app.content.all_pregen_combat_profiles import build_all_pregen_combat_profiles
from app.content.certified_heroes import (
    build_all_certified_hero_entries,
    build_certified_hero_entries,
)
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles


def test_public_canonical_registry_remains_2024_only() -> None:
    entries = build_certified_hero_entries()

    assert entries
    assert {template.ruleset for _, template in entries} == {"2024"}
    assert all(build_id == "canonical" for (class_id, level, build_id), template in entries)


def test_all_edition_registry_contains_exact_certified_2014_progressions() -> None:
    entries = build_all_certified_hero_entries()
    heroes_2014 = [(key, template) for key, template in entries if template.ruleset == "2014"]
    fighters = [(key, template) for key, template in heroes_2014 if key[0] == "fighter"]
    barbarians = [(key, template) for key, template in heroes_2014 if key[0] == "barbarian"]
    rogues = [(key, template) for key, template in heroes_2014 if key[0] == "rogue"]
    monks = [(key, template) for key, template in heroes_2014 if key[0] == "monk"]

    assert len(heroes_2014) == 50
    assert [key[1] for key, _ in fighters] == list(range(1, 21))
    assert [key[1] for key, _ in barbarians] == list(range(1, 11))
    assert [key[1] for key, _ in rogues] == list(range(1, 11))
    assert [key[1] for key, _ in monks] == list(range(1, 11))
    assert {key[2] for key, _ in heroes_2014} == {"canonical-2014"}
    assert {template.name for _, template in fighters} == {"Karnok Stoneward"}
    assert {template.name for _, template in barbarians} == {"Rokhan Stonefury"}
    assert {template.name for _, template in rogues} == {"Mara Quickstep"}
    assert {template.name for _, template in monks} == {"Kael Stillwater"}
    assert all(template.weapon_masteries == [] for _, template in heroes_2014)


def test_arena_fingerprints_stay_2024_while_all_edition_registry_adds_2014() -> None:
    arena_profiles = build_pregen_combat_profiles()
    all_profiles = build_all_pregen_combat_profiles()
    fighter_ids = {f"karnok-stoneward-2014-l{level}" for level in range(1, 21)}
    barbarian_ids = {f"rokhan-stonefury-2014-l{level}" for level in range(1, 11)}
    rogue_ids = {f"mara-quickstep-2014-l{level}" for level in range(1, 11)}
    monk_ids = {f"kael-stillwater-2014-l{level}" for level in range(1, 11)}
    ids_2014 = fighter_ids | barbarian_ids | rogue_ids | monk_ids

    assert ids_2014.isdisjoint(arena_profiles)
    assert ids_2014.issubset(all_profiles)
    assert set(all_profiles) == set(arena_profiles) | ids_2014


def test_2014_fighter_gets_source_derived_unarmed_opportunity_profile() -> None:
    hero = complete_unarmed_opportunity_profiles([build_karnok_stoneward_2014(5)])[0]
    profile = hero.unarmed_opportunity_attack

    assert profile is not None
    assert hero.ability_scores.strength == 18
    assert profile.attack_bonus == 7
    assert profile.damage == 5
