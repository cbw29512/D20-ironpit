from pathlib import Path

from app.content.json_combatant_compiler import (
    fold_hero_level,
    load_hero_progression,
    load_hero_track,
    load_species,
    load_subclass_progression,
)


ROOT = Path(__file__).resolve().parents[2]


def _fighter_sources():
    progression = load_hero_progression(ROOT / "data/heroes/2024/class_progressions/fighter.json")
    subclass = load_subclass_progression(ROOT / "data/heroes/2024/subclasses/champion.json")
    species = load_species(ROOT / "data/heroes/2024/species/orc.json")
    track = load_hero_track(ROOT / "data/heroes/2024/tracks/karnok-stoneward.json")
    return progression, subclass, species, track


def test_class_table_does_not_contain_character_stats():
    progression, _subclass, _species, _track = _fighter_sources()
    level1 = progression.levels[0].model_dump(exclude_none=True)
    assert "max_hp" not in level1
    assert "ability_scores" not in level1
    assert "adrenaline-rush" not in level1.get("resources", {})
    assert "savage-attacker" not in level1.get("capabilities_added", [])


def test_fighter_json_folds_static_state_and_level_deltas():
    progression, subclass, species, track = _fighter_sources()

    level3 = fold_hero_level(progression, subclass, species, track, 3)
    assert level3["ability_scores"]["strength"] == 17
    assert level3["max_hp"] == 28
    assert level3["resources"]["action-surge"] == 1
    assert level3["resources"]["adrenaline-rush"] == 2
    assert level3["resources"]["relentless-endurance"] == 1
    assert "improved-critical" in level3["capabilities"]
    assert "savage-attacker" in level3["capabilities"]
    assert "adrenaline-rush" in level3["capabilities"]

    level4 = fold_hero_level(progression, subclass, species, track, 4)
    assert level4["ability_scores"]["strength"] == 18
    assert level4["ability_scores"]["constitution"] == 16
    assert level4["resources"]["second-wind"] == 3
    assert level4["weapon_masteries"] == ["flail", "javelin", "spear", "longsword"]


def test_fighter_json_reuses_capabilities_and_replaces_subclass_feature():
    progression, subclass, species, track = _fighter_sources()

    level17 = fold_hero_level(progression, subclass, species, track, 17)
    assert level17["attack_count"] == 3
    assert level17["resources"]["action-surge"] == 2
    assert level17["resources"]["indomitable"] == 3
    assert level17["resources"]["adrenaline-rush"] == 6
    assert "superior-critical" in level17["capabilities"]
    assert "improved-critical" not in level17["capabilities"]

    level20 = fold_hero_level(progression, subclass, species, track, 20)
    assert level20["attack_count"] == 4
    assert "survivor-defy-death" in level20["capabilities"]
    assert "boon-combat-prowess" in level20["capabilities"]


def test_fighter_json_keeps_edition_and_subclass_explicit():
    progression, subclass, species, track = _fighter_sources()
    level20 = fold_hero_level(progression, subclass, species, track, 20)

    assert level20["edition"] == "2024"
    assert level20["class_id"] == "fighter"
    assert level20["subclass_id"] == "champion"
    assert level20["species_id"] == "orc"
