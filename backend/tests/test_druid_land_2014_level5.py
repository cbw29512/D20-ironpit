from __future__ import annotations

from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.druid_land_forest_2014_spells import forest_circle_spell_ids_2014


def test_level_five_druid_stats_resources_and_dispel_magic_binding() -> None:
    hero = build_thalen_greenbough_2014(5)

    assert hero.max_hp == 38
    assert hero.ability_scores.wisdom == 18
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 2,
        "wild-shape": 2,
    }
    assert hero.replacement_form_actions[0].form_template_id == "2014-crocodile"
    assert hero.skill_bonuses["insight"] == 7
    assert hero.skill_bonuses["religion"] == 4
    assert hero.skill_bonuses["perception"] == 7
    assert hero.skill_bonuses["survival"] == 7

    dispel = hero.effect_removal_actions[0]
    assert dispel.id == "dispel-magic"
    assert dispel.casting_ability == "wisdom"
    assert dispel.resource_id == "spell-slot-3"


def test_level_five_base_spell_package_has_nine_prepared_spells() -> None:
    package = build_druid_2014_spell_package(5, 4)

    assert len(package.cantrips) == 3
    assert len(package.spells) == 9
    assert package.spells[-1].id == "dispel-magic"


def test_level_five_forest_circle_spells_remain_fail_closed_until_call_lightning_is_supported() -> None:
    assert forest_circle_spell_ids_2014(5) == (
        "barkskin",
        "spider-climb",
        "call-lightning",
        "plant-growth",
    )
    audit = next(
        item for item in build_druid_land_2014_feature_audits(5)
        if item.feature_id == "circle-spells-3"
    )
    assert audit.combat_relevant is True
    assert audit.automated is False
