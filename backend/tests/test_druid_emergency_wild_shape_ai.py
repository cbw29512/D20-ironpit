from __future__ import annotations

from types import SimpleNamespace

from app.combat.replacement_form_policy import ai_may_start_replacement_form
from app.content.druid_2014_wild_shape import wild_shape_action_2014
from app.content.druid_2024_form_support import wild_shape_actions


def _state(current_hp: int, shaped: bool = False):
    return SimpleNamespace(
        current_hp=current_hp,
        replacement_form=object() if shaped else None,
    )


def test_2014_caster_druid_keeps_spellcasting_at_high_hp() -> None:
    action = wild_shape_action_2014(8)
    owner = SimpleNamespace(max_hp=60)
    assert action.action_cost == "action"
    assert action.hp_mode == "form_pool"
    assert action.ai_use_policy == "emergency_only"
    # Emergency transformation cannot require a setup spell or spell slot.
    assert action.setup_spell_id is None
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
