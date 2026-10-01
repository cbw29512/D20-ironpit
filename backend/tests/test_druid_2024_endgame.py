from __future__ import annotations

from app.combat.initiative_resource_refill import resolve_initiative_resource_refills
from app.combat.resource_conversion import automatic_resource_conversion, resolve_resource_conversion
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.content.replacement_form_compiler import compile_replacement_form_template
from app.content.replacement_form_registry import replacement_form_source_template
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _resource(state, resource_id: str):
    return next(item for item in state.resources if item.id == resource_id)


def test_druid_18_beast_spells_reuses_replacement_form_spell_allowlist() -> None:
    hero = build_thalen_greenbough_level(18)
    profile = build_thalen_greenbough_profile(18)
    package = canonical_spell_package("druid", 18, "2024", 5)
    action = hero.replacement_form_actions[0]
    source = replacement_form_source_template("2024", action.form_template_id)
    active = compile_replacement_form_template(
        hero,
        source,
        retain_spellcasting=action.retain_spellcasting,
        retained_spell_action_ids=action.retained_spell_action_ids,
        retain_creature_type=action.retain_creature_type,
        retain_hit_points=action.hp_mode == "retain_owner",
    )

    assert hero.max_hp == 93
    assert package is not None and len(package.spells) == 20
    assert package.spells[-1].id == "barkskin"
    assert action.retain_spellcasting is True
    assert "wall-of-stone" in action.retained_spell_action_ids
    assert {item.id for item in active.persistent_barrier_actions} == {"wall-of-stone"}
    assert "lands-aid" not in action.retained_spell_action_ids
    assert "natures-sanctuary" not in action.retained_spell_action_ids
    barkskin = next(item for item in hero.defensive_spell_actions if item.id == "barkskin")
    foresight = next(item for item in hero.defensive_spell_actions if item.id == "foresight")
    assert (barkskin.action_cost, barkskin.duration_minutes, barkskin.concentration) == (
        "bonus_action", 60, False,
    )
    assert barkskin.modifier_effects[0].minimum_value == 17
    assert foresight.priority > barkskin.priority
    assert_pregen_combat_stats(hero, build_pregen_combat_profiles()[hero.id])
    assert {item.feature_id for item in profile.feature_audits} >= {"beast-spells", "druid-combat-spell-l18"}


def test_druid_19_chooses_boon_of_fate_and_keeps_damage_caster_progression() -> None:
    hero = build_thalen_greenbough_level(19)
    profile = build_thalen_greenbough_profile(19)
    package = canonical_spell_package("druid", 19, "2024", 5)

    assert hero.max_hp == 98
    assert hero.ability_scores.intelligence == 14
    assert hero.skill_bonuses["nature"] == 13
    assert hero.skill_bonuses["religion"] == 8
    assert package is not None and len(package.spells) == 21
    assert package.spells[-1].id == "regenerate"
    assert _resource(build_combatant_state(hero), "boon-of-fate").current_uses == 1
    grant = hero.progression_features.resource_backed_d20_outcome_adjustments[0]
    assert (grant.source_id, grant.dice_count, grant.dice_size, grant.range_ft) == (
        "boon-of-fate", 2, 4, 60,
    )
    assert hero.initiative_resource_refill_grants[0].source_id == "boon-of-fate"
    assert {item.feature_id for item in profile.feature_audits} >= {"boon-of-fate", "druid-combat-spell-l19"}
    assert_pregen_combat_stats(hero, build_pregen_combat_profiles()[hero.id])


def test_druid_20_archdruid_reuses_initiative_refill_and_resource_conversion() -> None:
    template = build_thalen_greenbough_level(20)
    profile = build_thalen_greenbough_profile(20)
    package = canonical_spell_package("druid", 20, "2024", 5)
    hero = EncounterCombatant(
        combatant_id="thalen",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(template),
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[], hero_total_levels=20, monster_total_cr="0",
    )

    assert template.max_hp == 103
    assert package is not None and len(package.spells) == 22
    assert package.spells[-1].id == "ice-storm"
    conversions = {item.target_resource_id: item for item in template.resource_conversion_actions if item.id.startswith("nature-magician")}
    assert {item.source_cost for item in conversions.values()} == {1, 2, 3, 4}
    assert set(conversions) == {"spell-slot-2", "spell-slot-4", "spell-slot-6", "spell-slot-8"}

    _resource(hero.state, "spell-slot-8").current_uses = 0
    chosen = automatic_resource_conversion(hero.state, "1:thalen")
    assert chosen is not None and chosen.id == "nature-magician-level-8"
    resolve_resource_conversion(
        hero.state, chosen, sequence=1, round_number=1, actor_id="thalen", turn_key="1:thalen",
    )
    assert _resource(hero.state, "spell-slot-8").current_uses == 1
    assert _resource(hero.state, "wild-shape").current_uses == 0
    assert _resource(hero.state, "nature-magician-conversion").current_uses == 0

    _resource(hero.state, "wild-shape").current_uses = 0
    events, _ = resolve_initiative_resource_refills(2, setup)
    evergreen = next(item for item in events if item.feature_id == "evergreen-wild-shape")
    assert evergreen.resource_remaining == 1
    assert _resource(hero.state, "wild-shape").current_uses == 1
    assert {item.feature_id for item in profile.feature_audits} >= {"archdruid", "druid-combat-spell-l20"}
    assert_pregen_combat_stats(template, build_pregen_combat_profiles()[template.id])
