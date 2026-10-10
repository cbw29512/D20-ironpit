"""Death-only replacement-form lifecycle (source-neutral; Deva adopter pending)."""
from __future__ import annotations

from app.combat.instant_death import apply_terminal_death
from app.combat.replacement_form_lifecycle import revert_replacement_form_if_incapacitated
from app.combat.replacement_forms import enter_replacement_form, resolve_replacement_form_action
from app.combat.state import build_combatant_state
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.domain.replacement_form_actions import ReplacementFormAction


def _setup():
    source = canonical_wild_shape_template_2014(2).model_copy(update={
        "id": "owner-source", "kind": "monster", "name": "Arbitrary shapeshifter",
    })
    form = source.model_copy(update={"id": "owner-source--form-new-shape"})
    return source, form, build_combatant_state(source)


def test_death_only_form_does_not_revert_on_incapacitation() -> None:
    original, active, state = _setup()
    action = ReplacementFormAction(
        id="new-form", name="Printed Transform", action_cost="action",
        form_template_id="new-shape", voluntary_revert_action="action",
        hp_mode="retain_owner", ends_on_death=True,
        ends_on_incapacitated=False, source="2014 printed source",
    )
    assert not action.ends_on_incapacitated
    assert action.ends_on_death
    resolve_replacement_form_action(state, action, active)
    assert state.replacement_form is not None
    assert state.replacement_form.ends_on_death
    assert state.current_hp == original.max_hp

    state.is_unconscious = True
    assert revert_replacement_form_if_incapacitated(state) is False
    assert state.template.id == active.id
    state.is_unconscious = False

    assert apply_terminal_death(state) == "dead"
    assert state.is_dead and state.current_hp == 0
    assert state.template.id == original.id
    assert state.replacement_form is None
    assert apply_terminal_death(state) == "unchanged"
    fresh = build_combatant_state(original)
    assert not fresh.is_dead and fresh.template.id == original.id


def test_existing_incapacitation_form_keeps_its_death_policy() -> None:
    original, active, state = _setup()
    enter_replacement_form(
        state, source_id="wolf", source_name="Existing form",
        form_template=active, action_cost="action",
        ends_on_incapacitated=True, hp_mode="retain_owner",
    )
    assert not state.replacement_form.ends_on_death
    state.is_unconscious = True
    assert revert_replacement_form_if_incapacitated(state)
    assert state.replacement_form is None and state.template.id == original.id


def test_unrelated_form_remains_until_its_declared_end_condition() -> None:
    original, active, state = _setup()
    enter_replacement_form(
        state, source_id="persistent", source_name="Persistent",
        form_template=active, action_cost="action",
        hp_mode="retain_owner", ends_on_incapacitated=False,
    )
    state.is_unconscious = True
    assert revert_replacement_form_if_incapacitated(state) is False
    assert state.replacement_form is not None
