from __future__ import annotations

from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.druid_land_forest_2014_spells import forest_circle_spell_ids_2014


def test_level_nine_progression_and_resources() -> None:
    hero = build_thalen_greenbough_2014(9)

    assert hero.level == 9
    assert hero.max_hp == 66
    assert hero.ability_scores.wisdom == 20
    assert hero.replacement_form_actions[0].form_template_id == "2014-brown-bear"
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 1,
        "wild-shape": 2,
    }
    assert hero.skill_bonuses["insight"] == 9
    assert hero.skill_bonuses["religion"] == 5
    assert hero.skill_bonuses["perception"] == 9
    assert hero.skill_bonuses["survival"] == 9


def test_level_nine_prepared_spell_count_is_legal() -> None:
    package = build_druid_2014_spell_package(9, 5)

    assert len(package.spells) == 14
    assert package.spells[-1].id == "reincarnate"


def test_level_nine_forest_circle_spells_are_preserved_as_arena_neutral() -> None:
    assert forest_circle_spell_ids_2014(9) == (
        "barkskin",
        "spider-climb",
        "call-lightning",
        "plant-growth",
        "divination",
        "freedom-of-movement",
        "commune-with-nature",
        "tree-stride",
    )
    audit = next(
        item for item in build_druid_land_2014_feature_audits(9)
        if item.feature_id == "circle-spells-5"
    )
    assert audit.combat_relevant is False
    assert audit.automated is False
