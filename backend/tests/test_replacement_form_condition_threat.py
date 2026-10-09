"""Protective transformation is justified by actual condition defense, not extra HP."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.combat.replacement_form_condition_threat import (
    failure_chance, form_mitigates_disabling_save,
)
from app.combat.replacement_form_offense import defer_emergency_form_for_spell
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.replacement_form_registry import replacement_form_source_template
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import SpellSaveAction
from app.domain.targeting import AreaTargeting
from app.domain.grid import BattleMapDefinition, GridPosition


def _scenario(builder):
    owner = builder(8)
    defender = EncounterCombatant(
        combatant_id="defender", side="heroes", position_ft=0,
        state=build_combatant_state(owner),
    )
    defender.state.current_hp = int(owner.max_hp * 0.25)
    enemy = EncounterCombatant(
        combatant_id="threat", side="monsters", position_ft=10,
        state=build_combatant_state(owner),
    )
    form = owner.replacement_form_actions[0]
    source = replacement_form_source_template(owner.ruleset, form.form_template_id)
    setup = EncounterSetup(
        heroes=[defender], monsters=[enemy], hero_total_levels=8,
        monster_total_cr="0", ruleset=owner.ruleset,
    )
    return defender, enemy, setup, form, source


@pytest.mark.parametrize("builder", [build_thalen_greenbough_2014, build_thalen_greenbough_level])
def test_printed_disable_is_a_real_form_defense_only_with_condition_immunity(builder) -> None:
    defender, enemy, setup, form, source = _scenario(builder)
    action = SavingThrowAction(
        id="universal-stunning-save", name="Stun",
        save_ability="wisdom", dc=30, range_ft=60,
        failed_save_timed_effect=FailedSaveTimedEffect(effect_id="stunned", duration_rounds=2),
    )
    enemy.state.template = enemy.state.template.model_copy(update={
        "saving_throw_actions": [action], "spell_save_actions": [],
    })
    guarded = source.model_copy(update={"condition_immunities": ["stunned"]})
    with patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=guarded):
        assert failure_chance(defender, action) >= 0.5
        assert form_mitigates_disabling_save(defender, setup, form)
    with patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=source):
        assert not form_mitigates_disabling_save(defender, setup, form)
    enemy.position_ft = 100
    with patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=guarded):
        assert not form_mitigates_disabling_save(defender, setup, form)
    enemy.position_ft = 10
    enemy.state.is_dead = True
    with patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=guarded):
        assert not form_mitigates_disabling_save(defender, setup, form)


def test_spell_slot_and_real_target_gate_non_damage_save() -> None:
    defender, enemy, setup, form, source = _scenario(build_thalen_greenbough_level)
    spell = SpellSaveAction(
        id="universal-hold", name="Hold", level=3,
        save_ability="wisdom", dc=30, range_ft=60,
        failed_save_timed_effect=FailedSaveTimedEffect(effect_id="paralyzed", duration_rounds=2),
    )
    enemy.state.template = enemy.state.template.model_copy(update={
        "saving_throw_actions": [], "spell_save_actions": [spell],
    })
    guarded = source.model_copy(update={"condition_immunities": ["paralyzed"]})
    with patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=guarded):
        assert form_mitigates_disabling_save(defender, setup, form)
        for resource in enemy.state.resources:
            if resource.id.startswith("spell-slot-"):
                resource.current_uses = 0
        assert not form_mitigates_disabling_save(defender, setup, form)


def test_benefit_must_be_defensive_and_applies_before_spell_offense_ranking() -> None:
    defender, enemy, setup, form, source = _scenario(build_thalen_greenbough_level)
    spell = SpellSaveAction(
        id="universal-hold", name="Hold", level=0,
        save_ability="wisdom", dc=30, range_ft=60,
        failed_save_timed_effect=FailedSaveTimedEffect(effect_id="paralyzed", duration_rounds=2),
    )
    enemy.state.template = enemy.state.template.model_copy(update={
        "saving_throw_actions": [], "spell_save_actions": [spell],
    })
    guarded = source.model_copy(update={"condition_immunities": ["paralyzed"]})
    with (
        patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=guarded),
        patch("app.combat.replacement_form_offense.choose_auto_hit_spell", return_value=None),
        patch("app.combat.replacement_form_offense.choose_spell_attack", return_value=None),
        patch("app.combat.replacement_form_offense.choose_spell", return_value=None),
        patch("app.combat.replacement_form_offense.choose_concentration_repeat_save", return_value=None),
        patch("app.combat.replacement_form_offense.incoming_attack_pressure", return_value=0),
    ):
        assert form_mitigates_disabling_save(defender, setup, form)
        assert not defer_emergency_form_for_spell(defender, setup, form, "1:defender")
    enemy.state.template = enemy.state.template.model_copy(update={
        "spell_save_actions": [spell.model_copy(update={
            "failed_save_timed_effect": FailedSaveTimedEffect(effect_id="frightened", duration_rounds=2)
        })],
    })
    with patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=guarded):
        assert not form_mitigates_disabling_save(defender, setup, form)


def test_universal_grid_aoe_disabling_save_can_threaten_a_group() -> None:
    defender, enemy, setup, form, source = _scenario(build_thalen_greenbough_level)
    defender.state.position = GridPosition(x=6, y=4)
    enemy.state.position = GridPosition(x=3, y=4)
    ally = EncounterCombatant(
        combatant_id="ally", side="heroes", position_ft=5,
        state=build_combatant_state(build_thalen_greenbough_level(8)),
    )
    ally.state.position = GridPosition(x=7, y=4)
    setup.heroes.append(ally)
    setup.map_definition = BattleMapDefinition(id="control-test", width_squares=20, height_squares=10)
    spell = SpellSaveAction(
        id="area-paralysis", name="Area paralysis", level=0,
        save_ability="wisdom", dc=30, range_ft=60,
        area=AreaTargeting(shape="radius", origin="point", radius_ft=5),
        failed_save_timed_effect=FailedSaveTimedEffect(effect_id="paralyzed", duration_rounds=2),
    )
    enemy.state.template = enemy.state.template.model_copy(update={
        "saving_throw_actions": [], "spell_save_actions": [spell],
    })
    protected = source.model_copy(update={"condition_immunities": ["paralyzed"]})
    with patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=protected):
        assert form_mitigates_disabling_save(defender, setup, form), (
            "A real legal area placement can affect the defender even in a group"
        )
        # The shared AoE selector cannot choose an out-of-range protected
        # defender merely because the area could geometrically reach it.
        defender.state.position = GridPosition(x=18, y=4)
        assert not form_mitigates_disabling_save(defender, setup, form)
        defender.state.position = GridPosition(x=6, y=4)
        assert form_mitigates_disabling_save(defender, setup, form)
        enemy.state.is_dead = True
        assert not form_mitigates_disabling_save(defender, setup, form)


def test_legacy_radius_aoe_disabling_save_uses_ally_safe_placement() -> None:
    defender, enemy, setup, form, source = _scenario(build_thalen_greenbough_2014)
    ally = EncounterCombatant(
        combatant_id="ally", side="heroes", position_ft=5,
        state=build_combatant_state(build_thalen_greenbough_2014(8)),
    )
    setup.heroes.append(ally)
    enemy.position_ft = 30
    spell = SpellSaveAction(
        id="legacy-area-stun", name="Area stun", level=0,
        save_ability="wisdom", dc=30, range_ft=60, area_radius_ft=10,
        failed_save_timed_effect=FailedSaveTimedEffect(effect_id="stunned", duration_rounds=2),
    )
    enemy.state.template = enemy.state.template.model_copy(update={
        "saving_throw_actions": [], "spell_save_actions": [spell],
    })
    guarded = source.model_copy(update={"condition_immunities": ["stunned"]})
    with patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=guarded):
        assert form_mitigates_disabling_save(defender, setup, form)
        enemy.position_ft = 300
        assert not form_mitigates_disabling_save(defender, setup, form)


@pytest.mark.parametrize("builder", [build_thalen_greenbough_2014, build_thalen_greenbough_level])
def test_printed_area_save_uses_chosen_legal_targets_and_remaining_resource(builder) -> None:
    defender, enemy, setup, form, source = _scenario(builder)
    defender.state.position = GridPosition(x=6, y=4)
    enemy.state.position = GridPosition(x=3, y=4)
    ally = EncounterCombatant(
        combatant_id="ally", side="heroes", position_ft=5,
        state=build_combatant_state(builder(8)),
    )
    ally.state.position = GridPosition(x=7, y=4)
    setup.heroes.append(ally)
    setup.map_definition = BattleMapDefinition(id="printed-area", width_squares=20, height_squares=10)
    action = SavingThrowAction(
        id="area-stun", name="Stun cloud", action_cost="action",
        save_ability="wisdom", dc=30, range_ft=60, resource_id="spell-slot-3",
        area=AreaTargeting(shape="radius", origin="point", radius_ft=5),
        failed_save_timed_effect=FailedSaveTimedEffect(effect_id="stunned", duration_rounds=2),
    )
    enemy.state.template = enemy.state.template.model_copy(update={
        "saving_throw_actions": [action], "spell_save_actions": [],
    })
    guarded = source.model_copy(update={"condition_immunities": ["stunned"]})
    from app.combat.area_save_actions import choose_area_save

    with patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=guarded):
        selected = choose_area_save(enemy, setup, action_cost="action")
        assert selected is not None and defender.combatant_id in selected[1].target_ids
        assert form_mitigates_disabling_save(defender, setup, form)
        # The Action chooser is still legal, but its selected area omits this
        # distant combatant, so the form gets no condition-defense bonus.
        defender.state.position = GridPosition(x=18, y=4)
        assert not form_mitigates_disabling_save(defender, setup, form)
        defender.state.position = GridPosition(x=6, y=4)
        for resource in enemy.state.resources:
            if resource.id == "spell-slot-3":
                resource.current_uses = 0
        assert not form_mitigates_disabling_save(defender, setup, form)
        for resource in enemy.state.resources:
            if resource.id == "spell-slot-3":
                resource.current_uses = 1
        # Hearing requirements are filtered by the existing target legality
        # rule; a deafened defender must not be treated as affected.
        enemy.state.template.saving_throw_actions[0].requires_target_hearing = True
        defender.state.active_effect_ids.append("deafened")
        assert not form_mitigates_disabling_save(defender, setup, form)
        defender.state.active_effect_ids.remove("deafened")
    assert defender.state.current_hp == int(defender.state.template.max_hp * 0.25)


def test_printed_area_save_selection_not_an_arbitrary_reachable_geometry() -> None:
    defender, enemy, setup, form, source = _scenario(build_thalen_greenbough_level)
    defender.state.position = GridPosition(x=6, y=4)
    enemy.state.position = GridPosition(x=3, y=4)
    setup.map_definition = BattleMapDefinition(id="area-choice", width_squares=20, height_squares=10)
    action = SavingThrowAction(
        id="area-paralysis", name="Paralysis cloud", action_cost="action",
        save_ability="wisdom", dc=30, range_ft=60,
        area=AreaTargeting(shape="radius", origin="point", radius_ft=5),
        failed_save_timed_effect=FailedSaveTimedEffect(effect_id="paralyzed", duration_rounds=2),
    )
    # Another area Action wins the source selector based on target coverage;
    # its rider is harmless, so the dangerous unchosen spell is not forecast.
    other = action.model_copy(update={
        "id": "area-harmless", "damage_dice_count": 10, "damage_type": "force",
        "failed_save_timed_effect": None,
    })
    enemy.state.template = enemy.state.template.model_copy(update={
        "saving_throw_actions": [action, other], "spell_save_actions": [],
    })
    guarded = source.model_copy(update={"condition_immunities": ["paralyzed"]})
    with patch("app.combat.replacement_form_condition_threat.replacement_form_source_template", return_value=guarded):
        assert not form_mitigates_disabling_save(defender, setup, form)
