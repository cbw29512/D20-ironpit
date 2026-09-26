from __future__ import annotations

from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014


def test_level_eight_asi_caps_charisma_and_improves_constitution() -> None:
    hero = build_nyra_emberveil_2014(8)
    profile = build_nyra_emberveil_2014_profile(8)

    assert profile.final_ability_scores.charisma == 20
    assert profile.final_ability_scores.constitution == 12
    assert hero.max_hp == 50
    assert hero.saving_throw_bonuses["charisma"] == 8
    assert hero.saving_throw_bonuses["constitution"] == 4

    fire_bolt = next(item for item in hero.spell_attack_actions if item.id == "fire-bolt")
    fireball = next(item for item in hero.spell_save_actions if item.id == "fireball")
    assert fire_bolt.attack_bonus == 8
    assert fire_bolt.damage_bonus == 5
    assert fireball.dc == 16
    assert fireball.damage_bonus == 5


def test_level_eight_adds_second_fourth_level_slot_and_dispel_magic() -> None:
    hero = build_nyra_emberveil_2014(8)
    package = build_sorcerer_2014_spell_package(8)

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 2,
        "sorcery-points": 8,
    }
    assert len(package.spells) == 9
    assert package.spells[-1].id == "dispel-magic"
    assert [item.id for item in hero.effect_removal_actions] == ["dispel-magic"]
