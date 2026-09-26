from __future__ import annotations

from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014


def test_level_eight_wisdom_asi_and_brown_bear_wild_shape() -> None:
    hero = build_thalen_greenbough_2014(8)

    assert hero.level == 8
    assert hero.max_hp == 59
    assert hero.ability_scores.wisdom == 20
    assert hero.replacement_form_actions[0].form_template_id == "2014-brown-bear"
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 2,
        "wild-shape": 2,
    }
    assert hero.skill_bonuses["insight"] == 8
    assert hero.skill_bonuses["perception"] == 8
    assert hero.skill_bonuses["survival"] == 8


def test_level_eight_brown_bear_form_is_certified_cr_one() -> None:
    bear = canonical_wild_shape_template_2014(8)

    assert bear.id == "2014-brown-bear"
    assert bear.challenge_rating == "1"
    assert bear.ruleset == "2014"


def test_level_eight_prepared_spell_count_tracks_wisdom_twenty() -> None:
    package = build_druid_2014_spell_package(8, 5)

    assert len(package.spells) == 13
    assert package.spells[-2].id == "control-water"
    assert package.spells[-1].id == "locate-creature"


def test_level_eight_audits_certify_asi_and_wild_shape_improvement() -> None:
    audits = {item.feature_id: item for item in build_druid_land_2014_feature_audits(8)}

    assert audits["ability-score-improvement-8"].automated is True
    assert audits["wild-shape-improvement-8"].automated is True
