from __future__ import annotations

from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.replacement_form_compiler import compile_replacement_form_template
from app.content.replacement_form_registry import replacement_form_source_template


def _resources(level: int) -> dict[str, int]:
    hero = build_thalen_greenbough_2014(level)
    return {resource.id: resource.max_uses for resource in hero.resources}


def _compiled_form_spell_ids(level: int) -> set[str]:
    hero = build_thalen_greenbough_2014(level)
    action = hero.replacement_form_actions[0]
    source = replacement_form_source_template(hero.ruleset, action.form_template_id)
    active = compile_replacement_form_template(
        hero,
        source,
        retain_spellcasting=action.retain_spellcasting,
        retained_spell_action_ids=action.retained_spell_action_ids,
    )
    return {
        action.id
        for actions in (
            active.spell_save_actions,
            active.spell_attack_actions,
            active.persistent_spell_attack_actions,
            active.defensive_spell_actions,
            active.healing_actions,
            active.condition_removal_actions,
            active.effect_removal_actions,
        )
        for action in actions
    }


def test_level_eighteen_beast_spells_uses_replacement_form_spell_legality() -> None:
    hero = build_thalen_greenbough_2014(18)
    action = hero.replacement_form_actions[0]

    assert hero.level == 18
    assert hero.max_hp == 165
    assert action.retain_spellcasting is True
    assert set(action.retained_spell_action_ids) == {
        "produce-flame",
        "poison-spray",
        "faerie-fire",
        "healing-word",
        "cure-wounds",
        "lesser-restoration",
        "dispel-magic",
    }
    assert _compiled_form_spell_ids(18) == set(action.retained_spell_action_ids)
    assert _resources(18) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 3,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "spell-slot-9": 1,
        "wild-shape": 2,
    }

    audits = {item.feature_id: item for item in build_druid_land_2014_feature_audits(18)}
    assert audits["timeless-body"].combat_relevant is False
    assert audits["beast-spells"].combat_relevant is True
    assert audits["beast-spells"].automated is True

    package = build_druid_2014_spell_package(18, 5)
    assert len(package.spells) == 23
    assert package.spells[-1].id == "detect-poison-and-disease"


def test_level_nineteen_asi_recomputes_dexterity_derived_values() -> None:
    hero = build_thalen_greenbough_2014(19)

    assert hero.level == 19
    assert hero.max_hp == 174
    assert hero.ability_scores.dexterity == 17
    assert hero.armor_class == 16
    assert hero.initiative_bonus == 3
    assert _resources(19) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 3,
        "spell-slot-6": 2,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "spell-slot-9": 1,
        "wild-shape": 2,
    }

    audit = next(
        item for item in build_druid_land_2014_feature_audits(19)
        if item.feature_id == "ability-score-improvement-19"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True

    package = build_druid_2014_spell_package(19, 5)
    assert len(package.spells) == 24
    assert package.spells[-1].id == "purify-food-and-drink"


def test_level_twenty_archdruid_uses_unlimited_wild_shape_and_wider_spell_allowlist() -> None:
    hero = build_thalen_greenbough_2014(20)
    action = hero.replacement_form_actions[0]

    assert hero.level == 20
    assert hero.max_hp == 183
    assert "wild-shape" not in _resources(20)
    assert hero.unlimited_resource_ids == ["wild-shape"]
    assert action.retain_spellcasting is True
    assert set(action.retained_spell_action_ids) == {
        "produce-flame",
        "poison-spray",
        "faerie-fire",
        "healing-word",
        "cure-wounds",
        "lesser-restoration",
        "dispel-magic",
        "longstrider",
        "barkskin",
        "freedom-of-movement",
    }
    assert _compiled_form_spell_ids(20) == set(action.retained_spell_action_ids)
    assert _resources(20) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 3,
        "spell-slot-6": 2,
        "spell-slot-7": 2,
        "spell-slot-8": 1,
        "spell-slot-9": 1,
    }

    audit = next(
        item for item in build_druid_land_2014_feature_audits(20)
        if item.feature_id == "archdruid"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True

    package = build_druid_2014_spell_package(20, 5)
    assert len(package.spells) == 25
    assert package.spells[-1].id == "speak-with-animals"
