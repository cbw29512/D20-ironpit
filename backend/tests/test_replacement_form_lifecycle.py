from __future__ import annotations

import pytest

from app.combat.replacement_forms import enter_replacement_form, revert_replacement_form
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.druid_2014_wild_shape import wild_shape_action_2014
from app.content.replacement_form_compiler import compile_replacement_form_template
from app.domain.combatants import ResourceDefinition
from app.domain.modifiers import ConcentrationState


def _wolf_form(template):
    wolf = canonical_wild_shape_template_2014(2)
    return compile_replacement_form_template(template, wolf)


def test_replacement_form_spends_action_and_resource_but_preserves_concentration() -> None:
    template = build_thalen_greenbough_2014(1).model_copy(update={
        "resources": [ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=2)],
    })
    state = build_combatant_state(template)
    state.concentration = ConcentrationState(source_id="druid", effect_id="faerie-fire", started_round=0)

    result = enter_replacement_form(
        state,
        source_id="wild-shape",
        source_name="Wild Shape",
        form_template=_wolf_form(template),
        action_cost="action",
        resource_id="wild-shape",
    )

    assert state.action_available is False
    assert state.replacement_form is not None
    assert state.template.id.endswith("--form-2014-wolf")
    assert state.replacement_form.form_hp == state.template.max_hp
    assert state.resources[0].current_uses == 1
    assert state.concentration is not None
    assert state.concentration.effect_id == "faerie-fire"
    assert result.resource_remaining == 1


def test_voluntary_revert_uses_bonus_action_and_keeps_original_hp() -> None:
    template = build_thalen_greenbough_2014(1).model_copy(update={
        "resources": [ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=2)],
    })
    state = build_combatant_state(template)
    state.current_hp = 6
    enter_replacement_form(
        state,
        source_id="wild-shape",
        source_name="Wild Shape",
        form_template=_wolf_form(template),
        action_cost="action",
        resource_id="wild-shape",
    )
    state.bonus_action_available = True

    result = revert_replacement_form(state, spend_voluntary_action=True)

    assert result.reverted is True
    assert state.replacement_form is None
    assert state.template.id == template.id
    assert state.current_hp == 6
    assert state.bonus_action_available is False


def test_2014_wild_shape_declares_generic_incapacitation_reversion() -> None:
    action = wild_shape_action_2014(2)
    assert action.hp_mode == "form_pool"
    assert action.ends_on_incapacitated is True


def test_incapacitating_timed_condition_reverts_declared_form() -> None:
    template = build_thalen_greenbough_2014(2)
    state = build_combatant_state(template)
    action = wild_shape_action_2014(2)
    form = compile_replacement_form_template(
        template,
        canonical_wild_shape_template_2014(2),
    )
    enter_replacement_form(
        state,
        source_id=action.id,
        source_name=action.name,
        form_template=form,
        action_cost=action.action_cost,
        resource_id=action.resource_id,
        resource_cost=action.resource_cost,
        voluntary_revert_action=action.voluntary_revert_action,
        ends_on_incapacitated=action.ends_on_incapacitated,
    )

    applied = apply_timed_condition(
        state,
        "stunned",
        "test-source",
        source_effect_id="test-stun",
        applied_round=1,
        expires_round=2,
    )

    assert applied == "stunned"
    assert state.replacement_form is None
    assert state.template.id == template.id


def test_replacement_form_refresh_requires_explicit_permission() -> None:
    template = build_thalen_greenbough_2014(1).model_copy(update={
        "resources": [ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=2)],
    })
    state = build_combatant_state(template)
    form = _wolf_form(template)

    enter_replacement_form(
        state,
        source_id="test-form",
        source_name="Test Form",
        form_template=form,
        action_cost="bonus_action",
        resource_id="wild-shape",
    )
    state.bonus_action_available = True

    with pytest.raises(ValueError, match="already in a replacement form"):
        enter_replacement_form(
            state,
            source_id="test-form",
            source_name="Test Form",
            form_template=form,
            action_cost="bonus_action",
            resource_id="wild-shape",
        )


def test_declared_replacement_form_refresh_reuses_original_owner_and_refreshes_temp_hp() -> None:
    template = build_thalen_greenbough_2014(1).model_copy(update={
        "resources": [ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=2)],
    })
    state = build_combatant_state(template)
    state.current_hp = 6
    form = compile_replacement_form_template(
        template,
        canonical_wild_shape_template_2014(2),
        retain_hit_points=True,
    )

    enter_replacement_form(
        state,
        source_id="test-form",
        source_name="Test Form",
        form_template=form,
        action_cost="bonus_action",
        resource_id="wild-shape",
        hp_mode="retain_owner",
        temporary_hp_on_enter=2,
        replace_existing_form=True,
    )
    state.temporary_hp = 1
    state.bonus_action_available = True

    result = enter_replacement_form(
        state,
        source_id="test-form",
        source_name="Test Form",
        form_template=form,
        action_cost="bonus_action",
        resource_id="wild-shape",
        hp_mode="retain_owner",
        temporary_hp_on_enter=2,
        replace_existing_form=True,
    )

    assert result.resource_remaining == 0
    assert state.current_hp == 6
    assert state.temporary_hp == 2
    assert state.replacement_form is not None
    assert state.replacement_form.original_template.id == template.id
    assert state.template.id == form.id
    assert state.bonus_action_available is False

    revert_replacement_form(state, spend_voluntary_action=False)
    assert state.template.id == template.id
    assert state.current_hp == 6
