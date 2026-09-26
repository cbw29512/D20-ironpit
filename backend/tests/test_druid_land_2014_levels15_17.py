from __future__ import annotations

from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014


def _resources(level: int) -> dict[str, int]:
    hero = build_thalen_greenbough_2014(level)
    return {resource.id: resource.max_uses for resource in hero.resources}


def test_level_fifteen_opens_eighth_level_spell_slot() -> None:
    hero = build_thalen_greenbough_2014(15)

    assert hero.level == 15
    assert hero.max_hp == 123
    assert hero.ability_scores.constitution == 16
    assert hero.ability_scores.wisdom == 20
    assert _resources(15) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "wild-shape": 2,
    }
    package = build_druid_2014_spell_package(15, 5)
    assert len(package.spells) == 20
    assert package.spells[-1].id == "control-weather"
    assert package.spells[-1].spell_level == 8
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]


def test_level_sixteen_asi_recomputes_hit_points() -> None:
    hero = build_thalen_greenbough_2014(16)

    assert hero.level == 16
    assert hero.max_hp == 147
    assert hero.ability_scores.constitution == 18
    assert hero.ability_scores.wisdom == 20
    assert _resources(16) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "wild-shape": 2,
    }
    audit = next(
        item for item in build_druid_land_2014_feature_audits(16)
        if item.feature_id == "ability-score-improvement-16"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True

    package = build_druid_2014_spell_package(16, 5)
    assert len(package.spells) == 21
    assert package.spells[-1].id == "heroes-feast"
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]


def test_level_seventeen_opens_ninth_level_slot_and_pb_six() -> None:
    hero = build_thalen_greenbough_2014(17)

    assert hero.level == 17
    assert hero.max_hp == 156
    assert hero.ability_scores.constitution == 18
    assert hero.ability_scores.wisdom == 20
    assert hero.skill_bonuses["insight"] == 11
    assert hero.skill_bonuses["religion"] == 7
    assert hero.skill_bonuses["perception"] == 11
    assert hero.skill_bonuses["survival"] == 11
    assert _resources(17) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "spell-slot-9": 1,
        "wild-shape": 2,
    }
    package = build_druid_2014_spell_package(17, 5)
    assert len(package.spells) == 22
    assert package.spells[-1].id == "true-resurrection"
    assert package.spells[-1].spell_level == 9
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]
