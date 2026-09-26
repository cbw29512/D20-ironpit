from __future__ import annotations

from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014


def test_level_one_draconic_resilience_and_spellcasting() -> None:
    hero = build_nyra_emberveil_2014(1)
    profile = build_nyra_emberveil_2014_profile(1)
    package = build_sorcerer_2014_spell_package(1)

    assert profile.subclass_id == "draconic-bloodline"
    assert hero.armor_class == 14
    assert hero.max_hp == 7
    assert hero.saving_throw_bonuses["constitution"] == 2
    assert hero.saving_throw_bonuses["charisma"] == 5
    assert {resource.id: resource.max_uses for resource in hero.resources} == {"spell-slot-1": 2}
    assert [spell.id for spell in package.cantrips] == ["fire-bolt", "light", "mage-hand", "prestidigitation"]
    assert [spell.id for spell in package.spells] == ["burning-hands", "detect-magic"]


def test_level_one_spell_bindings_use_universal_attack_and_save_actions() -> None:
    hero = build_nyra_emberveil_2014(1)

    fire_bolt = next(action for action in hero.spell_attack_actions if action.id == "fire-bolt")
    assert fire_bolt.attack_bonus == 5
    assert fire_bolt.range_ft == 120
    assert fire_bolt.damage_dice_count == 1
    assert fire_bolt.damage_dice_size == 10

    burning_hands = next(action for action in hero.spell_save_actions if action.id == "burning-hands")
    assert burning_hands.dc == 13
    assert burning_hands.area is not None
    assert burning_hands.area.shape == "cone"
    assert burning_hands.area.length_ft == 15
    assert burning_hands.damage_dice_count == 3
    assert burning_hands.success_damage == "half"
