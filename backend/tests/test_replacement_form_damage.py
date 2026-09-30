from __future__ import annotations

from app.combat.replacement_forms import enter_replacement_form
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.replacement_form_registry import replacement_form_source_template
from app.content.replacement_form_compiler import compile_replacement_form_template
from app.domain.combatants import ResourceDefinition


class FixedDice:
    def roll(self, sides: int) -> int:
        return 10


def _state():
    template = build_thalen_greenbough_2014(1).model_copy(update={
        "resources": [ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=2)],
    })
    state = build_combatant_state(template)
    form = compile_replacement_form_template(
        template,
        canonical_wild_shape_template_2014(2),
    )
    enter_replacement_form(
        state,
        source_id="wild-shape",
        source_name="Wild Shape",
        form_template=form,
        action_cost="action",
        resource_id="wild-shape",
    )
    return state


def test_damage_is_absorbed_by_form_hp_before_original_hp() -> None:
    state = _state()
    original_hp = state.current_hp

    outcome = apply_damage(state, 5, dice=FixedDice())

    assert outcome == "damaged"
    assert state.current_hp == original_hp
    assert state.replacement_form is not None
    assert state.replacement_form.form_hp == state.template.max_hp - 5


def test_zero_form_hp_reverts_and_excess_damage_hits_original_body() -> None:
    state = _state()
    original_hp = state.current_hp

    form_hp = state.replacement_form.form_hp
    outcome = apply_damage(state, form_hp + 4, dice=FixedDice())

    assert outcome == "damaged"
    assert state.replacement_form is None
    assert state.current_hp == original_hp - 4


def test_exact_form_hp_damage_reverts_without_harming_original_body() -> None:
    state = _state()
    original_hp = state.current_hp

    form_hp = state.replacement_form.form_hp
    outcome = apply_damage(state, form_hp, dice=FixedDice())

    assert outcome == "damaged"
    assert state.replacement_form is None
    assert state.current_hp == original_hp


def test_retained_owner_hp_form_uses_temp_hp_then_owner_hp_without_auto_revert() -> None:
    template = build_thalen_greenbough_level(2)
    state = build_combatant_state(template)
    action = template.replacement_form_actions[0]
    source = replacement_form_source_template("2024", action.form_template_id)
    form = compile_replacement_form_template(
        template,
        source,
        retain_spellcasting=action.retain_spellcasting,
        retain_creature_type=action.retain_creature_type,
        retain_hit_points=action.hp_mode == "retain_owner",
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
        hp_mode=action.hp_mode,
        temporary_hp_on_enter=action.temporary_hp_on_enter,
    )

    assert state.template.max_hp == 13
    assert state.template.creature_type == "Humanoid"
    assert state.temporary_hp == 2
    assert state.current_hp == 13
    assert state.replacement_form is not None
    assert state.replacement_form.hp_mode == "retain_owner"

    outcome = apply_damage(state, 5, dice=FixedDice())

    assert outcome == "damaged"
    assert state.temporary_hp == 0
    assert state.current_hp == 10
    assert state.replacement_form is not None
    assert state.template.id.endswith("--form-srd-wolf")


def test_retained_owner_hp_form_reverts_when_owner_becomes_unconscious() -> None:
    template = build_thalen_greenbough_level(2)
    state = build_combatant_state(template)
    action = template.replacement_form_actions[0]
    source = replacement_form_source_template("2024", action.form_template_id)
    form = compile_replacement_form_template(
        template, source,
        retain_spellcasting=action.retain_spellcasting,
        retain_creature_type=action.retain_creature_type,
        retain_hit_points=True,
    )
    enter_replacement_form(
        state, source_id=action.id, source_name=action.name, form_template=form,
        action_cost=action.action_cost, resource_id=action.resource_id,
        resource_cost=action.resource_cost, voluntary_revert_action=action.voluntary_revert_action,
        hp_mode=action.hp_mode, temporary_hp_on_enter=action.temporary_hp_on_enter,
        ends_on_incapacitated=action.ends_on_incapacitated,
    )

    outcome = apply_damage(state, 15, dice=FixedDice())

    assert outcome == "unconscious"
    assert state.current_hp == 0
    assert state.is_unconscious is True
    assert state.replacement_form is None
    assert state.template.id == "thalen-greenbough-l2"
