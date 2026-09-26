from __future__ import annotations

from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014


def test_level_twelve_asi_recomputes_shared_character_math() -> None:
    hero = build_thalen_greenbough_2014(12)

    assert hero.level == 12
    assert hero.ability_scores.constitution == 16
    assert hero.ability_scores.wisdom == 20
    assert hero.max_hp == 99
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "wild-shape": 2,
    }

    audit = next(
        item for item in build_druid_land_2014_feature_audits(12)
        if item.feature_id == "ability-score-improvement-12"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True

    package = build_druid_2014_spell_package(12, 5)
    assert len(package.spells) == 17
    assert package.spells[-1].id == "wind-walk"
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]


def test_level_thirteen_adds_pb_and_seventh_level_slot_without_new_resolver() -> None:
    hero = build_thalen_greenbough_2014(13)

    assert hero.level == 13
    assert hero.max_hp == 107
    assert hero.ability_scores.constitution == 16
    assert hero.ability_scores.wisdom == 20
    assert hero.skill_bonuses["insight"] == 10
    assert hero.skill_bonuses["religion"] == 6
    assert hero.skill_bonuses["perception"] == 10
    assert hero.skill_bonuses["survival"] == 10
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "wild-shape": 2,
    }

    package = build_druid_2014_spell_package(13, 5)
    assert len(package.spells) == 18
    assert package.spells[-1].id == "mirage-arcane"
    assert package.spells[-1].spell_level == 7
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]
