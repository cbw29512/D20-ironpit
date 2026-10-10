from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from app.combat.replacement_form_policy import ai_may_start_replacement_form
from app.content.druid_2014_wild_shape import wild_shape_action_2014
from app.content.druid_2024_form_support import wild_shape_actions
from app.combat.replacement_form_triage import defer_self_healing_for_form
from app.combat.replacement_form_offense import favor_spell_over_emergency_form, defer_emergency_form_for_spell
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.domain.encounters import EncounterCombatant
from app.domain.healing_actions import HealingAction


def _state(current_hp: int, shaped: bool = False):
    return SimpleNamespace(
        current_hp=current_hp,
        replacement_form=object() if shaped else None,
        temporary_hp=0,
    )


def test_2014_caster_druid_keeps_spellcasting_at_high_hp() -> None:
    action = wild_shape_action_2014(8)
    owner = SimpleNamespace(max_hp=60)
    assert action.action_cost == "action"
    assert action.hp_mode == "form_pool"
    assert action.ai_use_policy == "emergency_only"
    # The optional setup remains source data, but emergency AI bypasses it.
    assert action.setup_spell_id == "faerie-fire"
    assert not ai_may_start_replacement_form(_state(60), action, owner)
    assert not ai_may_start_replacement_form(_state(21), action, owner)
    assert ai_may_start_replacement_form(_state(20), action, owner)
    assert not ai_may_start_replacement_form(_state(0), action, owner)


def test_2024_caster_druid_uses_only_low_health_temporary_hp_buffer() -> None:
    action = wild_shape_actions(8)[0]
    owner = SimpleNamespace(max_hp=60)
    assert action.action_cost == "bonus_action"
    assert action.hp_mode == "retain_owner"
    assert action.temporary_hp_on_enter == 8
    assert action.ai_use_policy == "emergency_only"
    assert not ai_may_start_replacement_form(_state(60), action, owner)
    assert ai_may_start_replacement_form(_state(20), action, owner)
    assert not ai_may_start_replacement_form(_state(20, shaped=True), action, owner)


def test_moon_and_future_melee_form_role_reuses_same_gate_without_name_dispatch() -> None:
    owner = SimpleNamespace(max_hp=60)
    moon2014_source = wild_shape_action_2014(8, ai_use_policy="tactical")
    moon2024_source = wild_shape_actions(8, ai_use_policy="tactical")[0]
    assert ai_may_start_replacement_form(_state(60), moon2014_source, owner)
    assert moon2014_source.setup_spell_id == "faerie-fire"
    assert ai_may_start_replacement_form(_state(60), moon2024_source, owner)
    # Pure gate does not grant a bonus-action cost or healing feature on its own.
    assert moon2014_source.action_cost == "action"
    assert moon2024_source.temporary_hp_on_enter == 8


def test_2024_emergency_compares_net_temp_hp_to_same_cost_self_healing() -> None:
    template = build_thalen_greenbough_level(8)
    state = build_combatant_state(template)
    state.current_hp = 10
    member = EncounterCombatant(combatant_id="druid-2024", side="heroes", position_ft=0, state=state)
    minor = HealingAction(id="minor", name="Minor", action_cost="bonus_action",
                          target_mode="self", dice_count=1, dice_size=4)
    major = minor.model_copy(update={"dice_count": 5, "dice_size": 8})
    assert defer_self_healing_for_form(member, minor, "1:druid-2024")
    assert not defer_self_healing_for_form(member, major, "1:druid-2024")
    state.temporary_hp = 8
    assert not ai_may_start_replacement_form(state, template.replacement_form_actions[0], template)
    assert not defer_self_healing_for_form(member, minor, "1:druid-2024")


def test_2014_emergency_form_competes_only_with_same_action_cost_healing() -> None:
    template = build_thalen_greenbough_2014(8)
    state = build_combatant_state(template)
    state.current_hp = 10
    member = EncounterCombatant(combatant_id="druid-2014", side="heroes", position_ft=0, state=state)
    cure = HealingAction(id="cure", name="Cure", action_cost="action",
                         target_mode="self", dice_count=1, dice_size=8)
    assert defer_self_healing_for_form(member, cure, "1:druid-2014")
    assert not defer_self_healing_for_form(
        member, cure.model_copy(update={"action_cost": "bonus_action"}), "1:druid-2014",
    )


def test_emergency_offense_score_preserves_critical_hp_override() -> None:
    assert favor_spell_over_emergency_form(20, 60, 1 / 3, 8, 14)
    assert not favor_spell_over_emergency_form(10, 60, 1 / 3, 8, 14)
    assert not favor_spell_over_emergency_form(20, 60, 1 / 3, 8, 7)
    assert not favor_spell_over_emergency_form(20, 60, 1 / 3, 0, 14)


def test_2024_caster_chooses_available_offense_before_low_value_form() -> None:
    template = build_thalen_greenbough_level(8)
    state = build_combatant_state(template)
    state.current_hp = int(template.max_hp * 0.25)
    actor = EncounterCombatant(combatant_id="cast-2024", side="heroes", position_ft=0, state=state)
    form = template.replacement_form_actions[0]
    spell = SimpleNamespace(action=SimpleNamespace(id="offense", action_cost="action"),
                            expected_damage=20)
    with (
        patch("app.combat.replacement_form_offense.choose_auto_hit_spell", return_value=None),
        patch("app.combat.replacement_form_offense.choose_spell_attack", return_value=None),
        patch("app.combat.replacement_form_offense.choose_spell", return_value=spell),
        patch("app.combat.replacement_form_offense.choose_concentration_repeat_save", return_value=None),
        patch("app.combat.replacement_form_offense.incoming_attack_pressure", return_value=0),
        patch("app.combat.replacement_form_offense.form_mitigates_disabling_save", return_value=False),
    ):
        assert defer_emergency_form_for_spell(actor, SimpleNamespace(), form, "1:cast-2024")
        assert not defer_emergency_form_for_spell(
            actor, SimpleNamespace(),
            form.model_copy(update={"retained_spell_action_ids": ["offense"]}), "1:cast-2024",
        )
        state.current_hp = 2
        assert not defer_emergency_form_for_spell(actor, SimpleNamespace(), form, "1:cast-2024")


def test_2014_form_competes_with_action_spell_but_not_bonus_spell() -> None:
    template = build_thalen_greenbough_2014(8)
    state = build_combatant_state(template)
    state.current_hp = int(template.max_hp * 0.25)
    actor = EncounterCombatant(combatant_id="cast-2014", side="heroes", position_ft=0, state=state)
    form = template.replacement_form_actions[0]
    spell = SimpleNamespace(action=SimpleNamespace(id="offense", action_cost="action"),
                            expected_damage=50)
    with (
        patch("app.combat.replacement_form_offense.choose_auto_hit_spell", return_value=None),
        patch("app.combat.replacement_form_offense.choose_spell_attack", return_value=None),
        patch("app.combat.replacement_form_offense.choose_spell", return_value=spell),
        patch("app.combat.replacement_form_offense.choose_concentration_repeat_save", return_value=None),
        patch("app.combat.replacement_form_offense.incoming_attack_pressure", return_value=0),
        patch("app.combat.replacement_form_offense.form_mitigates_disabling_save", return_value=False),
    ):
        assert defer_emergency_form_for_spell(actor, SimpleNamespace(), form, "1:cast-2014")
        spell.action.action_cost = "bonus_action"
        assert not defer_emergency_form_for_spell(actor, SimpleNamespace(), form, "1:cast-2014")
