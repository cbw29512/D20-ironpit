from __future__ import annotations

from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014


def test_level_four_asi_updates_derived_combat_values() -> None:
    hero = build_nyra_emberveil_2014(4)
    profile = build_nyra_emberveil_2014_profile(4)

    assert hero.level == 4
    assert profile.level == 4
    assert profile.character_name == "Nyra Emberveil"
    assert profile.final_ability_scores.charisma == 19
    assert hero.max_hp == 22
    assert hero.saving_throw_bonuses["charisma"] == 6

    fire_bolt = next(action for action in hero.spell_attack_actions if action.id == "fire-bolt")
    burning_hands = next(action for action in hero.spell_save_actions if action.id == "burning-hands")
    assert fire_bolt.attack_bonus == 6
    assert burning_hands.dc == 14


def test_level_four_resources_and_spell_package_match_progression() -> None:
    hero = build_nyra_emberveil_2014(4)
    package = build_sorcerer_2014_spell_package(4)

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "sorcery-points": 4,
    }
    assert [item.id for item in package.cantrips] == [
        "fire-bolt",
        "ray-of-frost",
        "poison-spray",
        "shocking-grasp",
        "light",
    ]
    assert [item.id for item in package.spells] == [
        "burning-hands",
        "magic-missile",
        "false-life",
        "shatter",
        "detect-magic",
    ]


def test_level_four_keeps_shared_metamagic_and_font_of_magic_bindings() -> None:
    hero = build_nyra_emberveil_2014(4)
    audits = {item.feature_id: item for item in build_nyra_emberveil_2014_profile(4).feature_audits}

    assert [item.id for item in hero.spell_save_disadvantage_options] == ["heightened-spell"]
    assert {item.id for item in hero.resource_conversion_actions} == {
        "create-spell-slot-1",
        "convert-spell-slot-1",
        "create-spell-slot-2",
        "convert-spell-slot-2",
    }
    assert audits["ability-score-improvement"].combat_relevant is True
    assert audits["ability-score-improvement"].automated is True
