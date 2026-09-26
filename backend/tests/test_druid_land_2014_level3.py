from __future__ import annotations

from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_land_forest_2014_spells import forest_circle_spell_ids_2014
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014


def test_level_three_forest_druid_adds_second_level_magic_without_changing_wolf_form() -> None:
    hero = build_thalen_greenbough_2014(3)

    assert hero.max_hp == 24
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 2,
        "wild-shape": 2,
    }
    assert hero.replacement_form_actions[0].form_template_id == "2014-wolf"
    assert {spell.id for spell in hero.defensive_spell_actions} == {"longstrider", "barkskin"}
    assert {action.id for action in hero.condition_removal_actions} == {"lesser-restoration"}


def test_level_three_forest_circle_spells_are_locked() -> None:
    assert forest_circle_spell_ids_2014(3) == ("barkskin", "spider-climb")
    barkskin = next(spell for spell in build_thalen_greenbough_2014(3).defensive_spell_actions if spell.id == "barkskin")
    assert barkskin.concentration is True
    assert barkskin.modifier_effects[0].kind == "armor-class-minimum"
    assert barkskin.modifier_effects[0].minimum_value == 16


def test_level_three_base_prepared_package_reaches_six_without_counting_circle_spells() -> None:
    package = build_druid_2014_spell_package(3, 3)
    assert len(package.spells) == 6
    assert package.spells[-1].id == "lesser-restoration"
    assert "barkskin" not in {spell.id for spell in package.spells}
