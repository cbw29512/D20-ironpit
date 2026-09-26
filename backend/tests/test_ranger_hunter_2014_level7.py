from __future__ import annotations

from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_level_seven_progression_and_steel_will_binding() -> None:
    hero = build_rowan_ashtrail_2014(7)
    profile = build_rowan_ashtrail_2014_profile(7)

    assert hero.level == 7
    assert hero.max_hp == 60
    assert hero.attack_action is not None and len(hero.attack_action.slots) == 2
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
    }

    steel_will = next(
        item for item in hero.progression_features.saving_throw_advantage_grants
        if item.source_id == "steel-will"
    )
    assert steel_will.source_name == "Steel Will"
    assert steel_will.required_effect_tags == ["frightened"]
    assert set(steel_will.abilities) == {
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
    }

    audit = next(item for item in profile.feature_audits if item.feature_id == "steel-will")
    assert audit.combat_relevant is True
    assert audit.automated is True


def test_level_seven_known_spell_count_is_legal() -> None:
    package = build_ranger_2014_spell_package(7)

    assert len(package.spells) == 5
    assert package.spells[-1].id == "locate-object"
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]
