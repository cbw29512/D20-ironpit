from __future__ import annotations

from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.content.druid_land_2014_profile import build_thalen_greenbough_2014_profile
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014


def test_level_four_druid_applies_wisdom_asi_and_crocodile_form() -> None:
    profile = build_thalen_greenbough_2014_profile(4)
    hero = build_thalen_greenbough_2014(4)

    assert profile.final_ability_scores.wisdom == 18
    assert hero.max_hp == 31
    assert hero.ability_scores.wisdom == 18
    assert hero.replacement_form_actions[0].form_template_id == "2014-crocodile"
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "wild-shape": 2,
    }
    assert hero.skill_bonuses["insight"] == 6
    assert hero.skill_bonuses["perception"] == 6
    assert hero.skill_bonuses["survival"] == 6


def test_level_four_crocodile_form_is_certified_cr_half() -> None:
    crocodile = canonical_wild_shape_template_2014(4)
    assert crocodile.id == "2014-crocodile"
    assert crocodile.challenge_rating == "1/2"
    assert crocodile.ruleset == "2014"


def test_level_four_base_spell_package_has_three_cantrips_and_eight_prepared_spells() -> None:
    package = build_druid_2014_spell_package(4, 4)
    assert [spell.id for spell in package.cantrips] == [
        "produce-flame", "poison-spray", "druidcraft",
    ]
    assert len(package.spells) == 8
    assert package.spells[-2].id == "darkvision"
    assert package.spells[-1].id == "locate-animals-or-plants"
