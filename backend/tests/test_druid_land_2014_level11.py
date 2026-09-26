from __future__ import annotations

from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.domain.models import DamageType


def test_level_eleven_progression_is_spell_tier_only() -> None:
    hero = build_thalen_greenbough_2014(11)

    assert hero.level == 11
    assert hero.max_hp == 80
    assert hero.ability_scores.wisdom == 20
    assert hero.damage_immunities == [DamageType.POISON]
    assert hero.replacement_form_actions[0].form_template_id == "2014-brown-bear"
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "wild-shape": 2,
    }
    assert hero.skill_bonuses["insight"] == 9
    assert hero.skill_bonuses["religion"] == 5
    assert hero.skill_bonuses["perception"] == 9
    assert hero.skill_bonuses["survival"] == 9


def test_level_eleven_prepared_spell_count_is_legal_without_fake_combat_binding() -> None:
    package = build_druid_2014_spell_package(11, 5)

    assert len(package.cantrips) == 4
    assert len(package.spells) == 16
    assert package.spells[-1].id == "find-the-path"
    assert package.spells[-1].spell_level == 6
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]
