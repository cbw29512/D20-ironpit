from app.content.certified_heroes import (
    build_all_certified_hero_entries,
    build_certified_hero_entries,
)


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
