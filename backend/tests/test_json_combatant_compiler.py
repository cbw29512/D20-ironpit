from pathlib import Path

from app.content.json_combatant_compiler import (
    fold_hero_level,
    load_hero_progression,
    load_subclass_progression,
)


ROOT = Path(__file__).resolve().parents[2]


def _fighter_sources():
    progression = load_hero_progression(ROOT / "data/heroes/2024/class_progressions/fighter.json")
    subclass = load_subclass_progression(ROOT / "data/heroes/2024/subclasses/champion.json")
    return progression, subclass


def test_fighter_json_folds_static_state_and_level_deltas():
    progression, subclass = _fighter_sources()

    level3 = fold_hero_level(progression, subclass, 3)
    assert level3["ability_scores"]["strength"] == 17
    assert level3["max_hp"] == 28
    assert level3["resources"]["action-surge"] == 1
    assert "improved-critical" in level3["capabilities"]

    level4 = fold_hero_level(progression, subclass, 4)
    assert level4["ability_scores"]["strength"] == 18
    assert level4["ability_scores"]["constitution"] == 16
    assert level4["resources"]["second-wind"] == 3


def test_fighter_json_reuses_capabilities_and_replaces_subclass_feature():
    progression, subclass = _fighter_sources()

    level17 = fold_hero_level(progression, subclass, 17)
    assert level17["attack_count"] == 3
    assert level17["resources"]["action-surge"] == 2
    assert level17["resources"]["indomitable"] == 3
    assert "superior-critical" in level17["capabilities"]
    assert "improved-critical" not in level17["capabilities"]

    level20 = fold_hero_level(progression, subclass, 20)
    assert level20["attack_count"] == 4
    assert "survivor-defy-death" in level20["capabilities"]
    assert "boon-combat-prowess" in level20["capabilities"]


def test_fighter_json_keeps_edition_and_subclass_explicit():
    progression, subclass = _fighter_sources()
    level20 = fold_hero_level(progression, subclass, 20)

    assert level20["edition"] == "2024"
    assert level20["class_id"] == "fighter"
    assert level20["subclass_id"] == "champion"
