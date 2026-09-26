from __future__ import annotations

from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014


def test_level_five_progression_adds_third_level_slots_and_scaled_fire_bolt() -> None:
    hero = build_nyra_emberveil_2014(5)
    profile = build_nyra_emberveil_2014_profile(5)

    assert hero.level == 5
    assert profile.level == 5
    assert hero.max_hp == 27
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 2,
        "sorcery-points": 5,
    }

    fire_bolt = next(action for action in hero.spell_attack_actions if action.id == "fire-bolt")
    assert fire_bolt.attack_bonus == 7
    assert fire_bolt.damage_dice_count == 2
    assert fire_bolt.damage_dice_size == 10


def test_level_five_fireball_uses_shared_area_save_damage_shape() -> None:
    hero = build_nyra_emberveil_2014(5)
    fireball = next(action for action in hero.spell_save_actions if action.id == "fireball")

    assert fireball.level == 3
    assert fireball.action_cost == "action"
    assert fireball.range_ft == 150
    assert fireball.area is not None
    assert fireball.area.shape == "radius"
    assert fireball.area.origin == "point"
    assert fireball.area.radius_ft == 20
    assert fireball.save_ability == "dexterity"
    assert fireball.dc == 15
    assert fireball.damage_dice_count == 8
    assert fireball.damage_dice_size == 6
    assert fireball.damage_type == "fire"
    assert fireball.success_damage == "half"
    assert fireball.upcast_dice_per_level == 1


def test_level_five_spell_package_is_six_known_spells() -> None:
    package = build_sorcerer_2014_spell_package(5)

    assert len(package.cantrips) == 5
    assert [item.id for item in package.spells] == [
        "burning-hands",
        "detect-magic",
        "comprehend-languages",
        "knock",
        "detect-thoughts",
        "fireball",
    ]
