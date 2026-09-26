from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.debuff_counters import debuff_is_countered
from app.combat.state import build_combatant_state
from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.domain.models import DamageType


def _typed_source(creature_type: str):
    return build_thalen_greenbough_2014(9).model_copy(
        update={
            "id": f"test-{creature_type}",
            "name": f"Test {creature_type.title()}",
            "creature_type": creature_type,
        },
    )


def test_level_ten_progression_and_natures_ward_bindings() -> None:
    hero = build_thalen_greenbough_2014(10)
    state = build_combatant_state(hero)

    assert hero.level == 10
    assert hero.max_hp == 73
    assert hero.ability_scores.wisdom == 20
    assert hero.damage_immunities == [DamageType.POISON]
    assert hero.replacement_form_actions[0].form_template_id == "2014-brown-bear"
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "wild-shape": 2,
    }

    ward_modifiers = [
        item for item in hero.passive_modifier_grants
        if item.source_id == "natures-ward"
    ]
    assert {item.condition_id for item in ward_modifiers} == {"charmed", "frightened"}
    assert all(set(item.source_creature_types) == {"elemental", "fey"} for item in ward_modifiers)

    ward_counters = [
        item.counter for item in hero.progression_features.passive_debuff_counter_grants
        if item.source_id == "natures-ward"
    ]
    assert {item.debuff_id for item in ward_counters} == {"poisoned", "disease"}
    assert all(item.source_scope == "any" for item in ward_counters)

    assert adjusted_damage_amount(17, DamageType.POISON, state) == 0
    assert debuff_is_countered(state, "poisoned") is True
    assert debuff_is_countered(state, "disease") is True


def test_natures_ward_source_type_checks_drive_charm_and_fear_results() -> None:
    state = build_combatant_state(build_thalen_greenbough_2014(10))
    fey = _typed_source("fey")
    elemental = _typed_source("elemental")
    humanoid = _typed_source("humanoid")

    assert condition_is_immune(state, "charmed", fey) is True
    assert condition_is_immune(state, "frightened", fey) is True
    assert condition_is_immune(state, "charmed", elemental) is True
    assert condition_is_immune(state, "frightened", elemental) is True
    assert condition_is_immune(state, "charmed", humanoid) is False
    assert condition_is_immune(state, "frightened", humanoid) is False


def test_level_ten_spell_count_and_audit_are_legal() -> None:
    package = build_druid_2014_spell_package(10, 5)
    assert len(package.spells) == 15
    assert package.spells[-1].id == "scrying"

    audit = next(
        item for item in build_druid_land_2014_feature_audits(10)
        if item.feature_id == "natures-ward"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True
