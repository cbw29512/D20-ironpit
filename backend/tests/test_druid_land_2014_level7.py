from __future__ import annotations

from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.druid_land_forest_2014_spells import forest_circle_spell_ids_2014


def test_level_seven_druid_progression_and_shared_freedom_of_movement() -> None:
    hero = build_thalen_greenbough_2014(7)

    assert hero.level == 7
    assert hero.max_hp == 52
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
        "wild-shape": 2,
    }
    freedom = next(item for item in hero.defensive_spell_actions if item.id == "freedom-of-movement")
    assert freedom.level == 4
    assert freedom.concentration is False
    signatures = {
        (
            effect.debuff_counter.debuff_id,
            effect.debuff_counter.source_scope,
            effect.debuff_counter.mode,
            effect.debuff_counter.movement_cost_ft,
        )
        for effect in freedom.modifier_effects
        if effect.debuff_counter is not None
    }
    assert ("difficult-terrain", "any", "prevent", 0) in signatures
    assert ("grappled", "nonmagical", "remove-with-movement", 5) in signatures


def test_level_six_and_seven_normal_prepared_spell_counts_are_legal() -> None:
    level_six = build_druid_2014_spell_package(6, 4)
    level_seven = build_druid_2014_spell_package(7, 4)

    assert len(level_six.spells) == 10
    assert level_six.spells[-1].id == "water-breathing"
    assert len(level_seven.spells) == 11
    assert level_seven.spells[-1].id == "water-walk"


def test_level_seven_forest_circle_spells_are_always_prepared_metadata() -> None:
    assert forest_circle_spell_ids_2014(7) == (
        "barkskin",
        "spider-climb",
        "call-lightning",
        "plant-growth",
        "divination",
        "freedom-of-movement",
    )
    audit = next(
        item for item in build_druid_land_2014_feature_audits(7)
        if item.feature_id == "circle-spells-4"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True
