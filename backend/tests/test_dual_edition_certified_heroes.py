from app.content.all_pregen_combat_profiles import build_all_pregen_combat_profiles
from app.content.certified_heroes import (
    build_all_certified_hero_entries,
    build_certified_hero_entries,
)
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_public_canonical_registry_remains_2024_only() -> None:
    entries = build_certified_hero_entries()

    assert entries
    assert {template.ruleset for _, template in entries} == {"2024"}
    assert all(build_id == "canonical" for (class_id, level, build_id), template in entries)


def test_all_edition_registry_contains_exact_2014_fighter_levels_one_through_ten() -> None:
    entries = build_all_certified_hero_entries()
    fighter_2014 = [
        (key, template)
        for key, template in entries
        if template.ruleset == "2014"
    ]

    assert len(fighter_2014) == 10
    assert [key[1] for key, _ in fighter_2014] == list(range(1, 11))
    assert {key[0] for key, _ in fighter_2014} == {"fighter"}
    assert {key[2] for key, _ in fighter_2014} == {"canonical-2014"}
    assert {template.name for _, template in fighter_2014} == {"Karnok Stoneward"}
    assert all(template.weapon_masteries == [] for _, template in fighter_2014)


def test_arena_fingerprints_stay_2024_while_all_edition_registry_adds_2014() -> None:
    arena_profiles = build_pregen_combat_profiles()
    all_profiles = build_all_pregen_combat_profiles()
    ids_2014 = {f"karnok-stoneward-2014-l{level}" for level in range(1, 11)}

    assert ids_2014.isdisjoint(arena_profiles)
    assert ids_2014.issubset(all_profiles)
    assert set(all_profiles) == set(arena_profiles) | ids_2014
